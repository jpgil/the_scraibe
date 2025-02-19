import re
import streamlit as st
import src.core as scraibe
import src.st_include.app_docs as app_docs
import src.st_include.app_users as app_users
import src.st_include.app_utils as app_utils

def set_ai_result(category, json) -> None:
    filename = app_docs.active_document()
    st.session_state[f'ai_{filename}_{category}'] = json

def ai_result(category) -> list:
    filename = app_docs.active_document()
    result = st.session_state.get(f'ai_{filename}_{category}', [])
    return result
    # st.write(type(result))
    # return result if isinstance(result, list) or isinstance(result, dict) else []


def infer_section_id(content, original):
    sections = re.findall(r'>>>>>ID#([\d_]+)(.*?)<<<<<ID#\1', content, re.DOTALL)
    
    for section_id, text in sections:
        if original in text:
            return section_id
    
    return None  # Return None if no match is found

@st.cache_data(ttl=3600)
def llm_grammar(content):
    result = scraibe.llm.review_grammar(content)
    return result


#
# Renders for Streamlit
# ---------------------
#


def render_none(*args, **kwargs) -> None:
    st.warning("Not implemented yet")
    
def render_configure_AI(*args, **kwargs) -> None:
    
    with st.form(key=__name__, border=False):
        st.write("The configurations below is optional and overrides default behaviour.")
        
        langs = ["Inferred from the document", "English", "Español", "Français", "Deutsch"]

        lang_selected = langs.index(scraibe.llm.lang) if scraibe.llm.lang in langs else 0
        scraibe.llm.lang = st.selectbox("[optional] Document language", langs, index=lang_selected)

        scraibe.llm.purpose = st.text_input("[optional] Main purpose of this document", value=scraibe.llm.purpose, help="""
    Describe in detail what is the main goal of this document. For example:

    - This is a technical document that propose team standards to implement CI/CD
    - This is the README of a git repository containing a website based on streamlit to solve problem X
            """)
        
        scraibe.llm.role = st.text_input("[optional] Your role in this document", value=scraibe.llm.role, help=""" 
    Describe any specific role you can have in this document. E.g:
    
    - A seasoned DevOps engineer 
    - The manager who reviews the content
    - Specialist in documentation formalisms 
            """)
        
        if st.form_submit_button("Submit"):
            filename = app_docs.active_document()
            docs = app_docs.load_documents()
            docs["documents"][filename]["role"] = scraibe.llm.role
            docs["documents"][filename]["purpose"] = scraibe.llm.purpose
            docs["documents"][filename]["lang"] = scraibe.llm.lang
            # st.write(docs["documents"][filename])
            app_docs.save_documents(docs)
            st.info("Configuration saved")
        

def render_review_grammar(*args, **kwargs) -> None:
    filename = app_docs.active_document()
    document_content = kwargs['document_content']
    if st.button("Review Grammar and Spelling"):
        with st.spinner("Let AI think ..."):
            json_result = scraibe.llm.review_grammar(document_content)#llm_grammar(content)
        set_ai_result('grammar', json_result)
    
    for entry in ai_result('grammar'):
        section_title, original, corrected = entry['section'], entry['original'], entry['corrected']
        
        if original == corrected:
            continue

        section_id = infer_section_id(document_content, original)

        if original in document_content:
            st.markdown(f'In **{section_title}**')
            cols = st.columns([4,4,1])
            with cols[0]:
                st.code(original, wrap_lines=True, language=None)
            cols[1].code(corrected, wrap_lines=True, language=None)
            
            if app_users.can_edit():
                if cols[2].button("Fix", key=f"fix_grammar_section_{section_id}_{original}"):
                    section_content = scraibe.extract_section(document_content, section_id)
                    new_section_content = section_content.replace(original, corrected)
                    scraibe.save_section(filename, section_id, app_users.user(), new_section_content )
                    st.session_state['fixed_grammar'] = st.session_state.get('fixed_grammar', [])
                    st.session_state['fixed_grammar'].append(corrected)
                    app_utils.notify("Fixed!")
        else:
            if corrected in st.session_state.get('fixed_grammar', []):
                st.info("Fixed!")
            else:
                st.info("Problem with ...")
                st.code(original, wrap_lines=True)
                try:
                    st.code(scraibe.extract_section(document_content, section_id), wrap_lines=True)
                except:
                    st.error(f"{section_id} also not found")

def render_content_assessment(*args, **kwargs) -> None:
    filename = app_docs.active_document()
    document_content = kwargs['document_content']
    if st.button("Content Assessment"):
        with st.spinner("Let AI think ..."):
            json_result = scraibe.llm.extract_content_assessment(document_content)#llm_grammar(content)
        set_ai_result('Assessment', json_result)
    
    criteria = ai_result('Assessment')
    # st.write(criteria)
    if len(criteria):
        st.markdown("### Summary")
        
        st.markdown("""
| Category | Content |
| --- | --- |
| Type of document | {type_of_document} |
| Purpose | {purpose} |
| Expected content | {expected_content} |
                    """.format(**criteria))

        st.markdown("### Evaluation")
        tdata = { "Criteria": [], "Score": []}
        tdata["Criteria"] = criteria['criteria']
        tdata["Score"] = [ c.split(":")[0] for c in criteria['assessment']]
        st.dataframe(tdata, hide_index=True, use_container_width=False)

        st.markdown("### Recommendations")
        for i in range(5):
            try:
                st.markdown(f"#### {criteria['criteria'][i]}")
                st.markdown(criteria['assessment'][i])
                st.markdown(f"*{criteria['recommendations'][i]}*")
            except:
                st.warning("Ahem... some AI answer was not right, try again.")
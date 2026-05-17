"""
Universal Document Chat - Streamlit Application
Main entry point for the RAG-powered document Q&A system.

NEW FEATURES:
- Persistent chat history (saved to disk)
- Document auto-summarization
- Streaming answer generation
- Multi-modal support (Images + Text)
"""

import streamlit as st
import os
import json
from datetime import datetime
from typing import List
import config

# Try to import MultiModalRAG, fallback to regular RAG if not available
try:
    from modules.multimodal_rag import MultiModalRAG
    USE_MULTIMODAL = True
except:
    from modules.rag_pipeline import RAGPipeline
    USE_MULTIMODAL = False


# Page configuration
st.set_page_config(
    page_title=config.APP_TITLE,
    page_icon=config.APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            color: #1f77b4;
            text-align: center;
            margin-bottom: 0.5rem;
        }
        .sub-header {
            font-size: 1.2rem;
            color: #666;
            text-align: center;
            margin-bottom: 2rem;
        }
        .source-box {
            background-color: #f0f2f6;
            padding: 1rem;
            border-radius: 0.5rem;
            margin-top: 0.5rem;
            border-left: 4px solid #1f77b4;
        }
        .stats-box {
            background-color: #e8f4f8;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 1rem 0;
        }
        .summary-box {
            background-color: #fff3cd;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 0.5rem 0;
            border-left: 4px solid #ffc107;
        }
        .stButton>button {
            width: 100%;
        }
    </style>
""", unsafe_allow_html=True)


# === FEATURE 1: Persistent Chat History ===

def save_chat_history():
    """Save chat history to disk (without images - they can't be serialized)."""
    chat_dir = os.path.join(config.DATA_DIR, "chat_history")
    os.makedirs(chat_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"chat_{timestamp}.json"
    filepath = os.path.join(chat_dir, filename)
    
    # Create a copy of chat history without PIL Image objects
    serializable_history = []
    for msg in st.session_state.chat_history:
        msg_copy = msg.copy()
        # Remove images as they can't be JSON serialized
        if 'images' in msg_copy:
            # Store only metadata about images, not the actual images
            msg_copy['images'] = [
                {
                    'metadata': img['metadata'],
                    'score': img['score']
                } for img in msg_copy.get('images', [])
            ]
        serializable_history.append(msg_copy)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': timestamp,
            'messages': serializable_history
        }, f, indent=2, ensure_ascii=False)
    
    return filename


def load_latest_chat_history():
    """Load the most recent chat history from disk."""
    chat_dir = os.path.join(config.DATA_DIR, "chat_history")
    
    if not os.path.exists(chat_dir):
        return []
    
    # Get all chat files
    chat_files = [f for f in os.listdir(chat_dir) if f.startswith('chat_') and f.endswith('.json')]
    
    if not chat_files:
        return []
    
    # Get the most recent file
    latest_file = sorted(chat_files)[-1]
    filepath = os.path.join(chat_dir, latest_file)
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('messages', [])
    except:
        return []


def export_chat_as_json():
    """Export current chat as downloadable JSON (without images)."""
    if not st.session_state.chat_history:
        return None
    
    # Create a copy without PIL Image objects
    serializable_history = []
    for msg in st.session_state.chat_history:
        msg_copy = msg.copy()
        # Remove images as they can't be JSON serialized
        if 'images' in msg_copy:
            # Store only metadata about images, not the actual images
            msg_copy['images'] = [
                {
                    'metadata': img['metadata'],
                    'score': img['score']
                } for img in msg_copy.get('images', [])
            ]
        serializable_history.append(msg_copy)
    
    chat_data = {
        'exported_at': datetime.now().isoformat(),
        'total_messages': len(st.session_state.chat_history),
        'messages': serializable_history
    }
    
    return json.dumps(chat_data, indent=2, ensure_ascii=False)


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'rag_pipeline' not in st.session_state:
        with st.spinner("🚀 Initializing AI models... This may take a minute on first run."):
            if USE_MULTIMODAL:
                st.session_state.rag_pipeline = MultiModalRAG()
            else:
                st.session_state.rag_pipeline = RAGPipeline()
    
    if 'chat_history' not in st.session_state:
        # Start with empty chat (don't auto-load previous)
        st.session_state.chat_history = []
    
    if 'uploaded_file_names' not in st.session_state:
        st.session_state.uploaded_file_names = set()
    
    if 'document_summaries' not in st.session_state:
        st.session_state.document_summaries = {}


def display_header():
    """Display the application header."""
    title = f"{config.APP_ICON} {config.APP_TITLE}"
    if USE_MULTIMODAL:
        title += " 🖼️"
    st.markdown(f'<div class="main-header">{title}</div>', unsafe_allow_html=True)
    subtitle = config.APP_SUBTITLE
    if USE_MULTIMODAL:
        subtitle += " + Images"
    st.markdown(f'<div class="sub-header">{subtitle}</div>', unsafe_allow_html=True)


def sidebar_controls():
    """Render sidebar with file upload and controls."""
    with st.sidebar:
        st.header("📁 Document Management")
        
        # File uploader
        uploaded_files = st.file_uploader(
            "Upload your documents",
            type=['pdf', 'txt', 'md', 'docx', 'csv'],
            accept_multiple_files=True,
            help="Supported formats: PDF, TXT, MD, DOCX, CSV"
        )
        
        # Process uploaded files
        if uploaded_files:
            new_files = [f for f in uploaded_files if f.name not in st.session_state.uploaded_file_names]
            
            if new_files:
                with st.spinner("Processing documents..."):
                    # Show processing status
                    status_placeholder = st.empty()
                    
                    status_placeholder.info(config.STATUS_EXTRACTING)
                    
                    # Process files
                    results = st.session_state.rag_pipeline.process_uploaded_files(new_files)
                    
                    # Update status
                    if results['success'] or results['files_processed'] > 0:
                        status_placeholder.success(config.STATUS_READY)
                        
                        # Update tracked files
                        for f in new_files:
                            if f.name not in [err.split()[0] for err in results['errors'] if 'already indexed' in err]:
                                st.session_state.uploaded_file_names.add(f.name)
                        
                        # Show summary
                        if results['files_processed'] > 0:
                            msg = f"✅ Processed {results['files_processed']} file(s), created {results['total_chunks']} chunks"
                            if results.get('images_processed', 0) > 0:
                                msg += f", extracted {results['images_processed']} images 🖼️"
                            st.success(msg)
                        
                        # === FEATURE 2: Generate document summaries ===
                        if results.get('summaries'):
                            st.session_state.document_summaries.update(results['summaries'])
                        
                        # Show errors if any
                        if results['errors']:
                            for error in results['errors']:
                                st.warning(error)
                    else:
                        status_placeholder.error(config.STATUS_ERROR)
                        for error in results['errors']:
                            st.error(error)
        
        st.divider()
        
        # === Display document summaries ===
        if st.session_state.document_summaries:
            st.header("📝 Document Summaries")
            for filename, summary in st.session_state.document_summaries.items():
                with st.expander(f"📄 {filename}"):
                    st.markdown(f'<div class="summary-box">{summary}</div>', unsafe_allow_html=True)
        
        st.divider()
        
        # Control buttons
        st.header("⚙️ Controls")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                # Save before clearing
                if st.session_state.chat_history:
                    save_chat_history()
                st.session_state.chat_history = []
                st.rerun()
        
        with col2:
            if st.button("🔄 Reset Docs", use_container_width=True):
                st.session_state.rag_pipeline.reset_documents()
                st.session_state.uploaded_file_names = set()
                st.session_state.chat_history = []
                st.session_state.document_summaries = {}
                st.success("Documents reset!")
                st.rerun()
        
        # === FEATURE 1: Export chat button ===
        if st.session_state.chat_history:
            st.divider()
            st.header("💾 Export")
            
            chat_json = export_chat_as_json()
            if chat_json:
                st.download_button(
                    label="📥 Download Chat History",
                    data=chat_json,
                    file_name=f"chat_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )


def display_chat():
    """Display the chat interface."""
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Display images if available (multimodal feature)
            if message["role"] == "assistant" and "images" in message and message["images"]:
                st.markdown("### 🖼️ Relevant Images:")
                cols = st.columns(min(len(message["images"]), 3))
                for idx, img_data in enumerate(message["images"][:3]):
                    with cols[idx]:
                        st.image(img_data['image'], width='stretch')
                        st.caption(f"Page {img_data['metadata']['page']} • Score: {img_data['score']:.2f}")
            
            # Display sources if available
            if message["role"] == "assistant" and "sources" in message and message["sources"]:
                display_sources(message["sources"])
    
    # Chat input
    if prompt := st.chat_input("Ask a question about your documents..."):
        # Add user message to chat
        st.session_state.chat_history.append({
            "role": "user",
            "content": prompt
        })
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # === FEATURE 3: Streaming answer generation ===
        with st.chat_message("assistant"):
            try:
                # Create placeholder for streaming
                answer_placeholder = st.empty()
                
                # Stream the answer
                full_answer = ""
                sources = []
                relevant_images = []
                
                with st.spinner("Thinking..."):
                    # Get images first if multimodal
                    if USE_MULTIMODAL:
                        try:
                            relevant_images = st.session_state.rag_pipeline._retrieve_images(prompt)
                        except:
                            pass
                    
                    # Stream text answer
                    for chunk in st.session_state.rag_pipeline.generate_answer_stream(
                        question=prompt,
                        chat_history=st.session_state.chat_history[:-1]
                    ):
                        if chunk.get('type') == 'token':
                            full_answer += chunk['content']
                            answer_placeholder.markdown(full_answer + "▌")
                        elif chunk.get('type') == 'done':
                            answer_placeholder.markdown(full_answer)
                            sources = chunk.get("sources", [])
                            break
                
                # Display images
                if relevant_images:
                    st.markdown("### 🖼️ Relevant Images:")
                    cols = st.columns(min(len(relevant_images), 3))
                    for idx, img_data in enumerate(relevant_images[:3]):
                        with cols[idx]:
                            st.image(img_data['image'], width='stretch')
                            st.caption(f"Page {img_data['metadata']['page']} • Score: {img_data['score']:.2f}")
                
                # Display sources
                if sources:
                    display_sources(sources)
                
                # Add to chat history
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": full_answer,
                    "sources": sources,
                    "images": relevant_images
                })
                
                # Auto-save chat history
                save_chat_history()
                
            except Exception as e:
                # Fallback to non-streaming if streaming fails
                st.warning(f"Streaming failed, using standard mode: {str(e)}")
                
                with st.spinner("Generating answer..."):
                    response = st.session_state.rag_pipeline.generate_answer(
                        question=prompt,
                        chat_history=st.session_state.chat_history[:-1]
                    )
                    
                    st.markdown(response["answer"])
                    
                    # Display images if available
                    if response.get("relevant_images"):
                        st.markdown("### 🖼️ Relevant Images:")
                        cols = st.columns(min(len(response["relevant_images"]), 3))
                        for idx, img_data in enumerate(response["relevant_images"][:3]):
                            with cols[idx]:
                                st.image(img_data['image'], width='stretch')
                                st.caption(f"Page {img_data['metadata']['page']} • Score: {img_data['score']:.2f}")
                    
                    if response.get("sources"):
                        display_sources(response["sources"])
                    
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": response["answer"],
                        "sources": response.get("sources", []),
                        "images": response.get("relevant_images", [])
                    })
                    
                    save_chat_history()


def display_sources(sources: List[dict]):
    """Display source citations."""
    if not sources:
        return
    
    st.markdown("---")
    st.markdown("**📚 Sources:**")
    
    for i, source in enumerate(sources, 1):
        file_icon = {
            'pdf': '📕',
            'txt': '📄',
            'md': '📝',
            'docx': '📘',
            'csv': '📊'
        }.get(source['file_type'], '📄')
        
        st.markdown(
            f"{file_icon} **{source['file_name']}** - {source['detail']} "
            f"(relevance: {source['score']:.2f})",
            help=f"Confidence score: {source['score']:.3f}"
        )


def main():
    """Main application function."""
    # Initialize session state
    initialize_session_state()
    
    # Display header
    display_header()
    
    # Sidebar controls
    sidebar_controls()
    
    # Main chat area
    st.markdown("---")
    
    # Check if documents are loaded
    stats = st.session_state.rag_pipeline.get_stats()
    
    if stats['total_chunks'] == 0:
        st.info("👈 Please upload some documents using the sidebar to get started!")
    else:
        display_chat()


if __name__ == "__main__":
    main()

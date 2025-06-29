"""
🦚 Peacock Memory - Import Functions
Import logic adapted from original basic-memory importers
"""

import hashlib
from datetime import datetime
from typing import Dict, Any, List
from core.database import get_client, get_or_create_collection

def import_claude_conversations(json_data: Dict[str, Any]) -> Dict[str, int]:
    """Import Claude conversations into ChromaDB"""
    try:
        conversations_imported = 0
        messages_imported = 0
        
        # Get or create conversations collection
        collection = get_or_create_collection(
            "conversations",
            {"type": "conversations", "source": "claude", "imported": datetime.now().isoformat()}
        )
        
        # Handle different conversation formats
        conversations = []
        
        if isinstance(json_data, list):
            conversations = json_data
        elif isinstance(json_data, dict):
            if 'conversations' in json_data:
                conversations = json_data['conversations']
            else:
                # Single conversation
                conversations = [json_data]
        
        for conversation in conversations:
            if not isinstance(conversation, dict):
                continue
            
            try:
                # Extract conversation metadata
                conv_id = conversation.get('uuid', conversation.get('id', f"conv_{conversations_imported}"))
                title = conversation.get('name', conversation.get('title', 'Untitled Conversation'))
                created_at = conversation.get('created_at', datetime.now().isoformat())
                
                # Extract messages
                messages = conversation.get('chat_messages', conversation.get('messages', []))
                
                if not messages:
                    continue
                
                # Combine all messages into conversation content
                conversation_content = []
                conversation_content.append(f"# Conversation: {title}")
                conversation_content.append(f"Created: {created_at}")
                conversation_content.append("")
                
                for i, message in enumerate(messages):
                    if not isinstance(message, dict):
                        continue
                    
                    # Handle different message formats
                    role = message.get('sender', message.get('role', 'unknown'))
                    content = message.get('text', message.get('content', ''))
                    
                    # Skip empty messages
                    if not content:
                        continue
                    
                    conversation_content.append(f"## {role.title()}")
                    conversation_content.append(content)
                    conversation_content.append("")
                    
                    messages_imported += 1
                
                # Create document ID
                doc_id = f"claude_conv_{hashlib.md5(conv_id.encode()).hexdigest()}"
                
                # Prepare metadata
                metadata = {
                    "conversation_id": conv_id,
                    "title": title,
                    "created_at": created_at,
                    "type": "conversation",
                    "source": "claude",
                    "message_count": len(messages),
                    "imported": datetime.now().isoformat()
                }
                
                # Add to collection
                collection.add(
                    documents=["\n".join(conversation_content)],
                    metadatas=[metadata],
                    ids=[doc_id]
                )
                
                conversations_imported += 1
                
            except Exception as e:
                print(f"Error importing conversation: {e}")
                continue
        
        return {
            "conversations": conversations_imported,
            "messages": messages_imported
        }
        
    except Exception as e:
        print(f"Error in Claude conversations import: {e}")
        return {"conversations": 0, "messages": 0}

def import_chatgpt_conversations(json_data: Dict[str, Any]) -> Dict[str, int]:
    """Import ChatGPT conversations into ChromaDB"""
    try:
        conversations_imported = 0
        messages_imported = 0
        
        # Get or create conversations collection
        collection = get_or_create_collection(
            "conversations",
            {"type": "conversations", "source": "chatgpt", "imported": datetime.now().isoformat()}
        )
        
        # Handle different conversation formats
        conversations = []
        
        if isinstance(json_data, list):
            conversations = json_data
        elif isinstance(json_data, dict):
            if 'conversations' in json_data:
                conversations = json_data['conversations']
            else:
                # Single conversation
                conversations = [json_data]
        
        for conversation in conversations:
            if not isinstance(conversation, dict):
                continue
            
            try:
                # Extract conversation metadata
                conv_id = conversation.get('conversation_id', conversation.get('id', f"chatgpt_conv_{conversations_imported}"))
                title = conversation.get('title', 'Untitled Conversation')
                create_time = conversation.get('create_time', datetime.now().timestamp())
                
                # Convert timestamp to ISO format
                if isinstance(create_time, (int, float)):
                    created_at = datetime.fromtimestamp(create_time).isoformat()
                else:
                    created_at = str(create_time)
                
                # Extract messages from mapping (ChatGPT format)
                mapping = conversation.get('mapping', {})
                
                if not mapping:
                    continue
                
                # Build message thread from mapping
                messages = []
                for node_id, node in mapping.items():
                    if not isinstance(node, dict):
                        continue
                    
                    message_data = node.get('message')
                    if not message_data:
                        continue
                    
                    # Extract message content
                    author = message_data.get('author', {})
                    role = author.get('role', 'unknown') if isinstance(author, dict) else str(author)
                    
                    content_data = message_data.get('content', {})
                    if isinstance(content_data, dict):
                        parts = content_data.get('parts', [])
                        content = '\n'.join(str(part) for part in parts if part)
                    else:
                        content = str(content_data)
                    
                    if content:
                        messages.append({
                            'role': role,
                            'content': content,
                            'node_id': node_id
                        })
                
                if not messages:
                    continue
                
                # Build conversation content
                conversation_content = []
                conversation_content.append(f"# Conversation: {title}")
                conversation_content.append(f"Created: {created_at}")
                conversation_content.append("")
                
                for message in messages:
                    role = message['role']
                    content = message['content']
                    
                    conversation_content.append(f"## {role.title()}")
                    conversation_content.append(content)
                    conversation_content.append("")
                    
                    messages_imported += 1
                
                # Create document ID
                doc_id = f"chatgpt_conv_{hashlib.md5(conv_id.encode()).hexdigest()}"
                
                # Prepare metadata
                metadata = {
                    "conversation_id": conv_id,
                    "title": title,
                    "created_at": created_at,
                    "type": "conversation",
                    "source": "chatgpt",
                    "message_count": len(messages),
                    "imported": datetime.now().isoformat()
                }
                
                # Add to collection
                collection.add(
                    documents=["\n".join(conversation_content)],
                    metadatas=[metadata],
                    ids=[doc_id]
                )
                
                conversations_imported += 1
                
            except Exception as e:
                print(f"Error importing ChatGPT conversation: {e}")
                continue
        
        return {
            "conversations": conversations_imported,
            "messages": messages_imported
        }
        
    except Exception as e:
        print(f"Error in ChatGPT conversations import: {e}")
        return {"conversations": 0, "messages": 0}

def import_claude_projects(json_data: Dict[str, Any]) -> Dict[str, int]:
    """Import Claude projects into ChromaDB"""
    try:
        projects_imported = 0
        documents_imported = 0
        
        # Handle different project formats
        projects = []
        
        if isinstance(json_data, list):
            projects = json_data
        elif isinstance(json_data, dict):
            if 'projects' in json_data:
                projects = json_data['projects']
            else:
                # Single project
                projects = [json_data]
        
        for project_data in projects:
            if not isinstance(project_data, dict):
                continue
            
            try:
                # Extract project metadata
                project_name = project_data.get('name', project_data.get('project_name', f"project_{projects_imported}"))
                description = project_data.get('description', '')
                created_at = project_data.get('created_at', datetime.now().isoformat())
                
                # Create project collection
                collection_name = f"project_{project_name}"
                collection = get_or_create_collection(
                    collection_name,
                    {
                        "type": "project",
                        "name": project_name,
                        "description": description,
                        "created": created_at,
                        "imported": datetime.now().isoformat()
                    }
                )
                
                # Extract documents
                documents = project_data.get('documents', project_data.get('knowledge_docs', []))
                
                for doc_data in documents:
                    if not isinstance(doc_data, dict):
                        continue
                    
                    try:
                        # Extract document data
                        doc_title = doc_data.get('title', doc_data.get('name', 'Untitled Document'))
                        doc_content = doc_data.get('content', doc_data.get('text', ''))
                        doc_type = doc_data.get('type', 'document')
                        
                        if not doc_content:
                            continue
                        
                        # Create document ID
                        doc_id = f"proj_doc_{hashlib.md5((project_name + doc_title).encode()).hexdigest()}"
                        
                        # Prepare metadata
                        metadata = {
                            "title": doc_title,
                            "type": "document",
                            "disposition": "Plan/Brainstorm",  # Default for project docs
                            "project": project_name,
                            "document_type": doc_type,
                            "created": doc_data.get('created_at', created_at),
                            "imported": datetime.now().isoformat()
                        }
                        
                        # Add to collection
                        collection.add(
                            documents=[doc_content],
                            metadatas=[metadata],
                            ids=[doc_id]
                        )
                        
                        documents_imported += 1
                        
                    except Exception as e:
                        print(f"Error importing document: {e}")
                        continue
                
                projects_imported += 1
                
            except Exception as e:
                print(f"Error importing project: {e}")
                continue
        
        return {
            "projects": projects_imported,
            "documents": documents_imported
        }
        
    except Exception as e:
        print(f"Error in Claude projects import: {e}")
        return {"projects": 0, "documents": 0}
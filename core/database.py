"""
🦚 Peacock Memory - Database Core
ChromaDB management and operations
"""

import chromadb
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
import hashlib

# Database path
DB_PATH = Path.home() / "peacock_db"

def get_client():
    """Get ChromaDB client"""
    DB_PATH.mkdir(exist_ok=True)
    return chromadb.PersistentClient(path=str(DB_PATH))

def get_or_create_collection(name: str, metadata: Optional[Dict] = None):
    """Get existing collection or create new one"""
    client = get_client()
    try:
        return client.get_collection(name)
    except:
        return client.create_collection(
            name=name,
            metadata=metadata or {"created": datetime.now().isoformat()}
        )

def add_file_to_collection(collection_name: str, file_path: str, content: str, disposition: str, project: Optional[str] = None):
    """Add file to specific collection"""
    collection = get_or_create_collection(collection_name)
    
    file_id = f"file_{hashlib.md5(file_path.encode()).hexdigest()}"
    metadata = {
        "file_path": file_path,
        "disposition": disposition,
        "type": "file",
        "created": datetime.now().isoformat(),
        "lines": len(content.split("\n")),
        "size": len(content)
    }
    
    if project:
        metadata["project"] = project
    
    # Determine language from file extension
    file_ext = Path(file_path).suffix.lower()
    lang_map = {
        ".py": "python", ".js": "javascript", ".html": "html", 
        ".css": "css", ".md": "markdown", ".txt": "text",
        ".sh": "bash", ".json": "json", ".yaml": "yaml",
        ".yml": "yaml", ".xml": "xml", ".sql": "sql"
    }
    metadata["language"] = lang_map.get(file_ext, "unknown")
    
    collection.add(
        documents=[content],
        metadatas=[metadata],
        ids=[file_id]
    )
    
    return file_id

def create_project(name: str, description: str = "") -> str:
    """Create new project collection"""
    collection_name = f"project_{name}"
    metadata = {
        "type": "project",
        "name": name,
        "description": description,
        "created": datetime.now().isoformat()
    }
    
    collection = get_or_create_collection(collection_name, metadata)
    return collection_name

def get_all_projects() -> List[Dict[str, Any]]:
    """Get all project collections"""
    client = get_client()
    collections = client.list_collections()
    
    projects = []
    for collection_info in collections:
        if collection_info.name.startswith("project_"):
            collection = client.get_collection(collection_info.name)
            metadata = collection.metadata or {}
            
            # Count items in project
            all_data = collection.get()
            item_count = len(all_data["documents"]) if all_data["documents"] else 0
            
            projects.append({
                "name": collection_info.name.replace("project_", ""),
                "collection_name": collection_info.name,
                "description": metadata.get("description", ""),
                "created": metadata.get("created", ""),
                "item_count": item_count
            })
    
    return projects

def get_project_contents(project_name: str) -> Dict[str, Any]:
    """Get all contents of a project"""
    collection_name = f"project_{project_name}"
    client = get_client()
    
    try:
        collection = client.get_collection(collection_name)
        all_data = collection.get()
        
        if not all_data["documents"]:
            return {"items": [], "count": 0}
        
        items = []
        for i, doc in enumerate(all_data["documents"]):
            metadata = all_data["metadatas"][i] if all_data["metadatas"] else {}
            items.append({
                "id": all_data["ids"][i],
                "content": doc,
                "metadata": metadata,
                "preview": doc[:200] + "..." if len(doc) > 200 else doc
            })
        
        return {
            "items": items,
            "count": len(items),
            "project_name": project_name
        }
    except:
        return {"items": [], "count": 0}

def search_all_collections(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Search across all collections"""
    client = get_client()
    collections = client.list_collections()
    
    results = []
    for collection_info in collections:
        collection = client.get_collection(collection_info.name)
        try:
            search_results = collection.query(
                query_texts=[query],
                n_results=min(limit, 5)
            )
            
            if search_results.get("documents") and search_results["documents"][0]:
                for i, doc in enumerate(search_results["documents"][0]):
                    metadata = search_results.get("metadatas", [[]])[0][i] if search_results.get("metadatas") else {}
                    distance = search_results.get("distances", [[]])[0][i] if search_results.get("distances") else 0
                    
                    results.append({
                        "collection": collection_info.name,
                        "document": doc,
                        "metadata": metadata,
                        "relevance": 1 - distance,
                        "preview": doc[:150] + "..." if len(doc) > 150 else doc
                    })
        except:
            continue
    
    # Sort by relevance
    results.sort(key=lambda x: x["relevance"], reverse=True)
    return results[:limit]

def search_by_type(query: str, search_type: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Search by specific type (codebase, conversations, ideas, etc.)"""
    client = get_client()
    collections = client.list_collections()
    
    # Type mapping
    type_filters = {
        "codebase": lambda meta: meta.get("disposition") == "Codebase",
        "conversations": lambda meta: meta.get("type") == "conversation",
        "ideas": lambda meta: meta.get("disposition") == "Idea",
        "brainstorm": lambda meta: meta.get("disposition") == "Plan/Brainstorm",
        "notes": lambda meta: meta.get("disposition") == "Note",
        "manpages": lambda meta: meta.get("disposition") == "man-page",
        "projects": lambda meta: meta.get("type") == "project"
    }
    
    if search_type not in type_filters:
        return []
    
    filter_func = type_filters[search_type]
    results = []
    
    for collection_info in collections:
        collection = client.get_collection(collection_info.name)
        try:
            search_results = collection.query(
                query_texts=[query],
                n_results=limit
            )
            
            if search_results.get("documents") and search_results["documents"][0]:
                for i, doc in enumerate(search_results["documents"][0]):
                    metadata = search_results.get("metadatas", [[]])[0][i] if search_results.get("metadatas") else {}
                    
                    # Apply type filter
                    if filter_func(metadata):
                        distance = search_results.get("distances", [[]])[0][i] if search_results.get("distances") else 0
                        
                        results.append({
                            "collection": collection_info.name,
                            "document": doc,
                            "metadata": metadata,
                            "relevance": 1 - distance,
                            "preview": doc[:150] + "..." if len(doc) > 150 else doc
                        })
        except:
            continue
    
    # Sort by relevance
    results.sort(key=lambda x: x["relevance"], reverse=True)
    return results[:limit]

def list_by_type(list_type: str) -> List[Dict[str, Any]]:
    """List all items of specific type"""
    client = get_client()
    collections = client.list_collections()
    
    type_filters = {
        "projects": lambda meta, name: name.startswith("project_"),
        "codebase": lambda meta, name: meta.get("disposition") == "Codebase",
        "conversations": lambda meta, name: meta.get("type") == "conversation",
        "ideas": lambda meta, name: meta.get("disposition") == "Idea",
        "brainstorm": lambda meta, name: meta.get("disposition") == "Plan/Brainstorm",
        "notes": lambda meta, name: meta.get("disposition") == "Note",
        "manpages": lambda meta, name: meta.get("disposition") == "man-page"
    }
    
    if list_type not in type_filters:
        return []
    
    filter_func = type_filters[list_type]
    results = []
    
    for collection_info in collections:
        collection = client.get_collection(collection_info.name)
        
        if list_type == "projects":
            if filter_func({}, collection_info.name):
                metadata = collection.metadata or {}
                all_data = collection.get()
                item_count = len(all_data["documents"]) if all_data["documents"] else 0
                
                results.append({
                    "name": collection_info.name.replace("project_", ""),
                    "collection_name": collection_info.name,
                    "description": metadata.get("description", ""),
                    "created": metadata.get("created", ""),
                    "item_count": item_count,
                    "type": "project"
                })
        else:
            try:
                all_data = collection.get()
                if all_data["documents"]:
                    for i, doc in enumerate(all_data["documents"]):
                        metadata = all_data["metadatas"][i] if all_data["metadatas"] else {}
                        
                        if filter_func(metadata, collection_info.name):
                            results.append({
                                "id": all_data["ids"][i],
                                "collection": collection_info.name,
                                "content": doc,
                                "metadata": metadata,
                                "preview": doc[:150] + "..." if len(doc) > 150 else doc,
                                "type": list_type
                            })
            except:
                continue
    
    return results

def delete_item(collection_name: str, item_id: str) -> bool:
    """Delete specific item from collection"""
    try:
        client = get_client()
        collection = client.get_collection(collection_name)
        collection.delete(ids=[item_id])
        return True
    except:
        return False

def delete_collection(collection_name: str) -> bool:
    """Delete entire collection"""
    try:
        client = get_client()
        client.delete_collection(collection_name)
        return True
    except:
        return False

def get_database_stats() -> Dict[str, Any]:
    """Get database statistics"""
    client = get_client()
    collections = client.list_collections()
    
    stats = {
        "total_collections": len(collections),
        "projects": 0,
        "total_documents": 0,
        "by_type": {
            "codebase": 0,
            "conversations": 0,
            "ideas": 0,
            "brainstorm": 0,
            "notes": 0,
            "manpages": 0
        }
    }
    
    for collection_info in collections:
        collection = client.get_collection(collection_info.name)
        all_data = collection.get()
        doc_count = len(all_data["documents"]) if all_data["documents"] else 0
        stats["total_documents"] += doc_count
        
        if collection_info.name.startswith("project_"):
            stats["projects"] += 1
        
        # Count by type
        if all_data["metadatas"]:
            for metadata in all_data["metadatas"]:
                if metadata:
                    disposition = metadata.get("disposition", "")
                    if disposition == "Codebase":
                        stats["by_type"]["codebase"] += 1
                    elif disposition == "Idea":
                        stats["by_type"]["ideas"] += 1
                    elif disposition == "Plan/Brainstorm":
                        stats["by_type"]["brainstorm"] += 1
                    elif disposition == "Note":
                        stats["by_type"]["notes"] += 1
                    elif disposition == "man-page":
                        stats["by_type"]["manpages"] += 1
                    elif metadata.get("type") == "conversation":
                        stats["by_type"]["conversations"] += 1
    
    return stats

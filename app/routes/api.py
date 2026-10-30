import os
import shutil
import uuid
from typing import Optional
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File, Form
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db, db_manager
from app import crud, config
from app.streaming import stream_video_file

router = APIRouter(prefix="/api", tags=["API"])

# Pydantic schemas for requests
class ReactionRequest(BaseModel):
    user_id: int
    reaction_type: str  # 'like' or 'dislike'

class CommentRequest(BaseModel):
    user_id: int
    content: str
    parent_id: Optional[int] = None

class HistoryRequest(BaseModel):
    user_id: int
    progress_seconds: Optional[int] = 0

class SubscribeRequest(BaseModel):
    user_id: int

# --- Stream Endpoint ---
@router.get("/stream/{filename}")
async def stream_video(filename: str, request: Request):
    clean_filename = Path(filename).name
    file_path = config.VIDEO_UPLOAD_DIR / clean_filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Video file not found")
    return stream_video_file(file_path, request)

# --- Videos ---
@router.get("/videos")
def list_videos(
    category: Optional[str] = None,
    q: Optional[str] = None,
    sort: str = "recent",
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    videos = crud.get_videos(db, category_slug=category, search_query=q, sort_by=sort, limit=limit, offset=offset)
    results = []
    for v in videos:
        results.append({
            "id": v.id,
            "title": v.title,
            "description": v.description,
            "video_url": v.video_url,
            "thumbnail_url": v.thumbnail_url,
            "duration": v.duration,
            "views_count": v.views_count,
            "likes_count": v.likes_count,
            "created_at": v.created_at.isoformat() if v.created_at else None,
            "channel": {
                "id": v.channel.id,
                "name": v.channel.channel_name,
                "handle": v.channel.handle,
                "avatar_url": v.channel.avatar_url,
                "verified": v.channel.verified
            } if v.channel else None,
            "category": v.category.name if v.category else None
        })
    return {"videos": results}

@router.get("/videos/{video_id}")
def get_video_detail(video_id: int, user_id: Optional[int] = None, db: Session = Depends(get_db)):
    video = crud.get_video_by_id(db, video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    user_reaction = None
    is_sub = False
    in_watch_later = False
    if user_id:
        user_reaction = crud.get_user_video_reaction(db, video_id, user_id)
        if video.channel:
            is_sub = crud.is_subscribed(db, user_id, video.channel.id)
        in_watch_later = crud.is_watch_later(db, user_id, video_id)

    # Related videos (same category or recent)
    related = crud.get_videos(db, category_slug=video.category.slug if video.category else None, limit=12)
    related_list = []
    for r in related:
        if r.id != video.id:
            related_list.append({
                "id": r.id,
                "title": r.title,
                "thumbnail_url": r.thumbnail_url,
                "duration": r.duration,
                "views_count": r.views_count,
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "channel_name": r.channel.channel_name if r.channel else "Unknown",
                "verified": r.channel.verified if r.channel else False
            })

    return {
        "id": video.id,
        "title": video.title,
        "description": video.description,
        "video_url": video.video_url,
        "thumbnail_url": video.thumbnail_url,
        "duration": video.duration,
        "views_count": video.views_count,
        "likes_count": video.likes_count,
        "dislikes_count": video.dislikes_count,
        "tags": video.tags,
        "created_at": video.created_at.isoformat() if video.created_at else None,
        "user_reaction": user_reaction,
        "is_subscribed": is_sub,
        "in_watch_later": in_watch_later,
        "channel": {
            "id": video.channel.id,
            "name": video.channel.channel_name,
            "handle": video.channel.handle,
            "avatar_url": video.channel.avatar_url,
            "banner_url": video.channel.banner_url,
            "subscribers": video.channel.subscriber_count,
            "verified": video.channel.verified
        } if video.channel else None,
        "category": {
            "id": video.category.id,
            "name": video.category.name,
            "slug": video.category.slug
        } if video.category else None,
        "related_videos": related_list
    }

@router.post("/videos/{video_id}/view")
def record_view(video_id: int, req: Optional[HistoryRequest] = None, db: Session = Depends(get_db)):
    views = crud.increment_views(db, video_id)
    if req and req.user_id:
        crud.record_watch_history(db, req.user_id, video_id, req.progress_seconds or 0)
    return {"success": True, "views_count": views}

@router.post("/videos/{video_id}/reaction")
def react_video(video_id: int, req: ReactionRequest, db: Session = Depends(get_db)):
    result = crud.react_to_video(db, video_id, req.user_id, req.reaction_type)
    return {"success": True, **result}

# --- Comments ---
@router.get("/videos/{video_id}/comments")
def get_comments(video_id: int, db: Session = Depends(get_db)):
    comments = crud.get_comments(db, video_id)
    results = []
    for c in comments:
        results.append({
            "id": c.id,
            "content": c.content,
            "likes_count": c.likes_count,
            "created_at": c.created_at.isoformat() if c.created_at else None,
            "user": {
                "id": c.user.id,
                "name": c.user.full_name,
                "username": c.user.username,
                "avatar_url": c.user.avatar_url
            } if c.user else None
        })
    return {"comments": results, "total": len(results)}

@router.post("/videos/{video_id}/comments")
def post_comment(video_id: int, req: CommentRequest, db: Session = Depends(get_db)):
    if not req.content.strip():
        raise HTTPException(status_code=400, detail="Comment cannot be empty")
    c = crud.add_comment(db, video_id, req.user_id, req.content.strip(), req.parent_id)
    return {
        "success": True,
        "comment": {
            "id": c.id,
            "content": c.content,
            "likes_count": c.likes_count,
            "created_at": c.created_at.isoformat() if c.created_at else None,
            "user": {
                "id": c.user.id,
                "name": c.user.full_name,
                "username": c.user.username,
                "avatar_url": c.user.avatar_url
            }
        }
    }

@router.delete("/comments/{comment_id}")
def delete_comment(comment_id: int, user_id: int, db: Session = Depends(get_db)):
    ok = crud.delete_comment(db, comment_id, user_id)
    if not ok:
        raise HTTPException(status_code=403, detail="Not authorized or comment not found")
    return {"success": True}

# --- Subscriptions ---
@router.post("/channels/{channel_id}/subscribe")
def toggle_sub(channel_id: int, req: SubscribeRequest, db: Session = Depends(get_db)):
    res = crud.toggle_subscription(db, req.user_id, channel_id)
    return {"success": True, **res}

# --- Watch Later ---
@router.post("/videos/{video_id}/watch-later")
def toggle_wl(video_id: int, req: SubscribeRequest, db: Session = Depends(get_db)):
    in_wl = crud.toggle_watch_later(db, req.user_id, video_id)
    return {"success": True, "saved": in_wl}

# --- History ---
@router.get("/history")
def get_user_history(user_id: int, db: Session = Depends(get_db)):
    items = crud.get_watch_history(db, user_id)
    results = []
    for item in items:
        v = item["video"]
        h = item["history"]
        results.append({
            "history_id": h.id,
            "watched_at": h.watched_at.isoformat() if h.watched_at else None,
            "video": {
                "id": v.id,
                "title": v.title,
                "thumbnail_url": v.thumbnail_url,
                "duration": v.duration,
                "views_count": v.views_count,
                "channel_name": v.channel.channel_name if v.channel else "Unknown"
            }
        })
    return {"history": results}

@router.post("/history/clear")
def clear_history(req: SubscribeRequest, db: Session = Depends(get_db)):
    crud.clear_watch_history(db, req.user_id)
    return {"success": True, "message": "History cleared"}

# --- Upload Studio ---
@router.post("/upload")
async def upload_video(
    title: str = Form(...),
    description: str = Form(""),
    category_id: Optional[int] = Form(None),
    tags: str = Form(""),
    user_id: int = Form(...),
    video_url_input: Optional[str] = Form(None),
    video_file: Optional[UploadFile] = File(None),
    thumbnail_file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    user = crud.get_user_by_id(db, user_id)
    if not user or not user.channel:
        raise HTTPException(status_code=400, detail="User or associated channel not found")

    # 1. Video handling
    final_video_url = ""
    duration_str = "2:30"
    duration_sec = 150

    if video_file and video_file.filename:
        ext = Path(video_file.filename).suffix.lower()
        if ext not in [".mp4", ".webm", ".mov", ".mkv", ".m4v"]:
            ext = ".mp4"
        unique_name = f"vid_{uuid.uuid4().hex[:12]}{ext}"
        target_path = config.VIDEO_UPLOAD_DIR / unique_name
        with open(target_path, "wb") as f_out:
            shutil.copyfileobj(video_file.file, f_out)
        final_video_url = f"/api/stream/{unique_name}"
    elif video_url_input and video_url_input.strip():
        final_video_url = video_url_input.strip()
    else:
        # Fallback to local sample
        final_video_url = "/static/uploads/videos/sample_nature_flower.mp4"

    # 2. Thumbnail handling
    final_thumb_url = ""
    if thumbnail_file and thumbnail_file.filename:
        ext = Path(thumbnail_file.filename).suffix.lower()
        if ext not in [".jpg", ".jpeg", ".png", ".webp", ".svg"]:
            ext = ".jpg"
        thumb_name = f"thumb_{uuid.uuid4().hex[:12]}{ext}"
        target_thumb = config.THUMBNAIL_UPLOAD_DIR / thumb_name
        with open(target_thumb, "wb") as f_out:
            shutil.copyfileobj(thumbnail_file.file, f_out)
        final_thumb_url = f"/static/uploads/thumbnails/{thumb_name}"
    else:
        # Default placeholder thumbnail
        final_thumb_url = "/static/uploads/thumbnails/thumb_code.jpg"

    video = crud.create_video(
        db=db,
        channel_id=user.channel.id,
        title=title,
        description=description,
        video_url=final_video_url,
        thumbnail_url=final_thumb_url,
        duration=duration_str,
        duration_seconds=duration_sec,
        category_id=category_id,
        tags=tags,
        visibility="public"
    )

    return {
        "success": True,
        "video_id": video.id,
        "message": "Video published successfully to MySQL database!"
    }

# --- Users list ---
@router.get("/users")
def get_users_list(db: Session = Depends(get_db)):
    users = crud.get_all_users(db)
    return {
        "users": [
            {
                "id": u.id,
                "username": u.username,
                "full_name": u.full_name,
                "avatar_url": u.avatar_url,
                "channel_id": u.channel.id if u.channel else None,
                "channel_name": u.channel.channel_name if u.channel else None,
                "handle": u.channel.handle if u.channel else None
            }
            for u in users
        ]
    }

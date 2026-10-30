from pathlib import Path
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db, db_manager
from app import crud

BASE_DIR = Path(__file__).resolve().parent.parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

router = APIRouter(include_in_schema=False)

@router.get("/")
def home_page(request: Request, category: str = "all", q: str = "", sort: str = "recent", db: Session = Depends(get_db)):
    categories = crud.get_categories(db)
    videos = crud.get_videos(db, category_slug=category, search_query=q, sort_by=sort)
    all_users = crud.get_all_users(db)
    db_status = db_manager.get_status()

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "active_page": "home",
            "categories": categories,
            "selected_category": category,
            "search_query": q,
            "selected_sort": sort,
            "videos": videos,
            "users": all_users,
            "db_status": db_status
        }
    )

@router.get("/watch")
def watch_page(request: Request, v: int, db: Session = Depends(get_db)):
    video = crud.get_video_by_id(db, v)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    crud.increment_views(db, v)
    comments = crud.get_comments(db, v)
    related = crud.get_videos(db, category_slug=video.category.slug if video.category else None, limit=12)
    related = [r for r in related if r.id != video.id]
    all_users = crud.get_all_users(db)
    db_status = db_manager.get_status()

    return templates.TemplateResponse(
        request=request,
        name="watch.html",
        context={
            "video": video,
            "comments": comments,
            "related_videos": related,
            "users": all_users,
            "db_status": db_status
        }
    )

@router.get("/channel/{handle}")
def channel_page(request: Request, handle: str, db: Session = Depends(get_db)):
    channel = crud.get_channel_by_handle(db, handle)
    if not channel and handle.isdigit():
        channel = crud.get_channel_by_id(db, int(handle))
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    videos = [v for v in channel.videos if v.visibility == "public"]
    all_users = crud.get_all_users(db)
    db_status = db_manager.get_status()

    return templates.TemplateResponse(
        request=request,
        name="channel.html",
        context={
            "channel": channel,
            "videos": videos,
            "users": all_users,
            "db_status": db_status
        }
    )

@router.get("/subscriptions")
def subscriptions_page(request: Request, db: Session = Depends(get_db)):
    all_users = crud.get_all_users(db)
    primary_user = all_users[0] if all_users else None
    videos = crud.get_subscriptions_videos(db, primary_user.id) if primary_user else []
    db_status = db_manager.get_status()

    return templates.TemplateResponse(
        request=request,
        name="subscriptions.html",
        context={
            "active_page": "subscriptions",
            "videos": videos,
            "users": all_users,
            "db_status": db_status
        }
    )

@router.get("/history")
def history_page(request: Request, db: Session = Depends(get_db)):
    all_users = crud.get_all_users(db)
    primary_user = all_users[0] if all_users else None
    history_items = crud.get_watch_history(db, primary_user.id) if primary_user else []
    db_status = db_manager.get_status()

    return templates.TemplateResponse(
        request=request,
        name="history.html",
        context={
            "active_page": "history",
            "history_items": history_items,
            "users": all_users,
            "db_status": db_status
        }
    )

@router.get("/liked")
def liked_page(request: Request, db: Session = Depends(get_db)):
    all_users = crud.get_all_users(db)
    primary_user = all_users[0] if all_users else None
    videos = crud.get_liked_videos(db, primary_user.id) if primary_user else []
    db_status = db_manager.get_status()

    return templates.TemplateResponse(
        request=request,
        name="liked.html",
        context={
            "active_page": "liked",
            "videos": videos,
            "users": all_users,
            "db_status": db_status
        }
    )

@router.get("/database")
def database_page(request: Request, db: Session = Depends(get_db)):
    all_users = crud.get_all_users(db)
    db_status = db_manager.get_status()

    return templates.TemplateResponse(
        request=request,
        name="database.html",
        context={
            "active_page": "database",
            "users": all_users,
            "db_status": db_status
        }
    )

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.graph import GraphResponse, GraphSummaryResponse
from app.services.graph_service import GraphBuildError, GraphNotFoundError, GraphService

router = APIRouter(prefix="/graph", tags=["graph"])
service = GraphService()


@router.get("", response_model=GraphResponse)
def get_global_graph(db: Session = Depends(get_db)) -> GraphResponse:
    try:
        return service.get_global_graph(db=db)
    except GraphBuildError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected server error occurred.",
        ) from exc


@router.get("/summary", response_model=GraphSummaryResponse)
def get_global_graph_summary(db: Session = Depends(get_db)) -> GraphSummaryResponse:
    try:
        return service.get_graph_summary(db=db)
    except GraphBuildError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected server error occurred.",
        ) from exc


@router.get("/{document_id}", response_model=GraphResponse)
def get_document_graph(document_id: int, db: Session = Depends(get_db)) -> GraphResponse:
    try:
        return service.get_document_graph(db=db, document_id=document_id)
    except GraphNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except GraphBuildError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected server error occurred.",
        ) from exc


@router.get("/{document_id}/summary", response_model=GraphSummaryResponse)
def get_document_graph_summary(document_id: int, db: Session = Depends(get_db)) -> GraphSummaryResponse:
    try:
        return service.get_graph_summary(db=db, document_id=document_id)
    except GraphNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except GraphBuildError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected server error occurred.",
        ) from exc

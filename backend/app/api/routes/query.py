from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.query import GraphQueryRequest, GraphQueryResponse
from app.services.graph_service import GraphBuildError, GraphNotFoundError
from app.services.query_service import InvalidQuestionError, QueryService

router = APIRouter(prefix="/query", tags=["query"])
service = QueryService()


@router.post("", response_model=GraphQueryResponse)
def run_query(request: GraphQueryRequest, db: Session = Depends(get_db)) -> GraphQueryResponse:
    try:
        return service.answer_question(db=db, question=request.question, document_id=request.document_id)
    except InvalidQuestionError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except GraphNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except GraphBuildError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected server error occurred.",
        ) from exc

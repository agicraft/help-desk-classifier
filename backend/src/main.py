from contextlib import asynccontextmanager
import logging
import os
from fastapi import FastAPI

from .classifier.classifier_service import CLASSIFIER_SERVICE_NAME, ClassifierService
from .classifier import classifier_router

logging.basicConfig(level=os.environ.get("LOG_LEVEL", "WARNING").upper())

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):

    yield {CLASSIFIER_SERVICE_NAME: ClassifierService()}


app = FastAPI(lifespan=lifespan, root_path=os.environ["API_BASE_URI"])

app.include_router(classifier_router.router)


@app.get("/")
def version():
    return {"version": "1.0.0"}

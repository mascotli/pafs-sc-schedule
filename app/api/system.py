from fastapi import APIRouter

from app.utils import R

v1 = APIRouter(prefix="/api/system", tags=["v1"], )


@v1.get("/job/statistic")
async def job_statistic():
    """
    home
    """
    from app.job.scheduler import job_scheduler
    return R.resp_200(data=job_scheduler.statistic())


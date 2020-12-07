from anonapi.client import AnonClientTool
from anonapi.objects import RemoteAnonServer
from anonapi.paths import UNCMapping, UNCMap, UNCPath
from celery import shared_task
from django.conf import settings
from idis.pipeline.models import Stream
from idissend.core import Stage
from idissend.persistence import IDISSendRecords, get_db_sessionmaker
from idissend.pipeline import IDISPipeline
from idissend.stages import CoolDown, PendingAnon, IDISConnection, Trash
from pathlib import Path


@shared_task
def run_pipeline_once():
    """Check for new files, send to IDIS, send finished on to final distination, etc.
    """

    pipeline = init_pipeline()
    pipeline.incoming.assert_all_paths()
    pipeline.run_once()


def init_pipeline() -> IDISPipeline:
    """Initialise a default pipeline based on django settings
    """

    # parameters #
    BASE_PATH = Path(
        settings.PIPELINE_BASE_PATH
    )  # all data for all stages goes here
    STAGES_BASE_PATH = BASE_PATH / "stages"

    # use this to identify with IDIS web API
    IDIS_USERNAME = settings.PIPELINE_IDIS_USERNAME
    IDIS_TOKEN = settings.PIPELINE_IDIS_TOKEN

    # Talk to IDIS through this connection
    IDIS_WEB_API_SERVER_NAME = settings.PIPELINE_IDIS_WEB_API_SERVER_NAME
    IDIS_WEB_API_SERVER_URL = settings.PIPELINE_IDIS_WEB_API_SERVER_URL

    RECORDS_DB_URL = settings.PIPELINE_RECORDS_DB_URL

    # init #
    STAGES_BASE_PATH.mkdir(
        parents=True, exist_ok=True
    )  # assert base dir exists

    # Indicate which local paths correspond to which UNC paths.
    # This makes it possible to expose local data to IDIS servers
    unc_mapping = UNCMapping(
        [
            UNCMap(
                local=Path(settings.PIPELINE_LOCAL_PATH),
                unc=UNCPath(settings.PIPELINE_UNC_PATH),
            )
        ]
    )

    # streams #
    # the different routes data can take through the pipeline. Data will always stay
    # inside the same stream
    streams = list(Stream.objects.all())

    # stages #
    # data in one stream goes through one or more of these stages
    incoming = CoolDown(
        name="incoming",
        path=STAGES_BASE_PATH / "incoming",
        streams=streams,
        cool_down=5,
    )

    cooled_down = Stage(
        name="cooled_down",
        path=STAGES_BASE_PATH / "cooled_down",
        streams=streams,
    )

    connection = IDISConnection(
        client_tool=AnonClientTool(username=IDIS_USERNAME, token=IDIS_TOKEN),
        servers=[
            RemoteAnonServer(
                name=IDIS_WEB_API_SERVER_NAME, url=IDIS_WEB_API_SERVER_URL
            )
        ],
    )

    records = IDISSendRecords(
        session_maker=get_db_sessionmaker(RECORDS_DB_URL)
    )

    pending = PendingAnon(
        name="pending",
        path=STAGES_BASE_PATH / "pending",
        streams=streams,
        idis_connection=connection,
        records=records,
        unc_mapping=unc_mapping,
    )

    errored = Stage(
        name="errored", path=STAGES_BASE_PATH / "errored", streams=streams
    )

    finished = CoolDown(
        name="finished",
        path=STAGES_BASE_PATH / "finished",
        streams=streams,
        cool_down=2 * 60 * 24,
    )  # 2 days

    trash = Trash(
        name="trash", path=STAGES_BASE_PATH / "trash", streams=streams
    )

    pipeline = IDISPipeline(
        incoming=incoming,
        cooled_down=cooled_down,
        pending=pending,
        finished=finished,
        trash=trash,
        errored=errored,
    )
    return pipeline

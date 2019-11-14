from datetime import datetime
from amshared.driverpack import DriverPack
from amshared.stage import _default_xtrameta_pack
from amshared.stage.constants import MK_CTIME, XTRA_CTIME_FORMAT


def test_xtrameta_ctime():
    tolerance = 3  # sec
    dp = DriverPack(_default_xtrameta_pack)
    time_string = dp[MK_CTIME].metadata[MK_CTIME]
    date_time = datetime.strptime(time_string, XTRA_CTIME_FORMAT)
    delta = datetime.utcnow() - date_time
    assert delta.total_seconds() < tolerance

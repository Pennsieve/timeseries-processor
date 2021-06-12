import os

from base_processor.settings import Settings


class DatabaseSettings(Settings):
    def __init__(self, use_ssl=True):
        super(DatabaseSettings, self).__init__()

        self.use_ssl = use_ssl

        env = self.environment
        self._load_values(
            postgres_db='{}-data-postgres-db'.format(env),
            postgres_host='{}-data-postgres-host'.format(env),
            postgres_password='{}-postgres-password'.format(env),
            postgres_port='{}-postgres-port'.format(env),
            postgres_user='{}-postgres-user'.format(env),
            s3_bucket_timeseries='{}-timeseries-s3-bucket'.format(env)
        )

        # compile postgres connection string
        self.postgres_connection_string = \
            "postgresql://{user}:{passw}@{host}:{port}/{db}" \
            .format(
                user=self.postgres_user,
                passw=self.postgres_password,
                host=self.postgres_host,
                port=self.postgres_port,
                db=self.postgres_db
            )

        # max serialized asset size, in mb
        self.timeseries_batch_size_mb = 1
        # max threads for network IO (s3 transfer)
        self.timeseries_max_write_threads = 8

        self.append_mode = os.environ.get('WRITE_MODE', '').upper() == "APPEND"

from timeseries_exporter import TimeSeriesExporter


if __name__ == "__main__":
    task = TimeSeriesExporter(cli=True)
    task.run()

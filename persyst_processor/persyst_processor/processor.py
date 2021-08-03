from base_processor.timeseries import BaseTimeSeriesProcessor
import base_processor.timeseries.utils as utils
import numpy as np

import ConfigParser
import time
import os
import numpy as np

import persyst


def multiply(x, calibration):
    return x * calibration


class PersystProcessor(BaseTimeSeriesProcessor):

    def task(self):
        """
        Reads Persyst file format, creates channel objects,
        and writes data (segment by segment) to TS DB.

        NOTE: SampleTimes/segments are in layout file, and represent timepoints of
        samples and the current time. The number preceding the equals symbol
        represents the number of samples processed since the start of the segment,
        and the number following it represents the start time of the segment in
        seconds (after midnight).

        NOTE: In our samples, the testtime header field does not match the time
        start time of the first segment (but it does in online examples). So we
        interpret start time here as the header start date plus the number of
        seconds elapsed since midnight before the first sample.

        NOTE: To take into account gaps between segments: Segment start times must
        be computed by adding the epoch date to the starting timestamp (after
        midnight). Segment end times must be computed by dividing samples
        processed (from next segment - current segment) by sample rate and adding to the start time.
        """
        self.LOGGER.info('Persyst Task started')

        files = self.inputs.get('file')

        # Initialize parser for layout, a .lay configuration file (.ini format)
        config = ConfigParser.RawConfigParser(allow_no_value=True)

        layout_path = persyst.find_lay(config, files)
        data_path = persyst.find_dat(files)

        # Check if file paths exist
        if layout_path is None:
            raise Exception('No .lay file provided')
        if data_path is None:
            raise Exception('No .dat file provided')

        config.read(layout_path)

        # Parse layout file for header properties
        header_name = persyst.get_config_section('FileInfo', config)['file']
        header_rate = float(persyst.get_config_section('FileInfo', config)['samplingrate'])
        header_datatype = int(persyst.get_config_section('FileInfo', config)['datatype'])
        header_calibration = float(persyst.get_config_section('FileInfo', config)['calibration'])

        try:
            header_date = persyst.get_config_section('Patient', config)['testdate']
            header_time = persyst.get_config_section('Patient', config)['testtime']

            # Compute epoch seconds from given header_date (midnight UTC)
            header_epoch = time.mktime(time.strptime(header_date, "%m/%d/%y"))
        except:
            header_epoch = 0

        # Get channels and channel info
        channel_rows = config.items('ChannelMap')
        num_channels = len(channel_rows)

        # Parse EEG binary, a .dat file, into numpy
        if header_datatype == 7:
            precision = 'int32'
            BYTE_SIZE = 4
        else:
            precision = 'int16'
            BYTE_SIZE = 2

        data_size = os.stat(data_path).st_size  # size of EEG binary in bytes
        num_samples = (data_size / num_channels) / BYTE_SIZE
        data = np.memmap(data_path,
                         dtype=precision,
                         mode='r',
                         shape=(num_channels, num_samples),
                         order='f')

        # Write all channel info (layout + binary data)
        for i, channel_tuple in enumerate(channel_rows):

            self.LOGGER.debug('Writing Channel: ' + str(i))

            # Get EEG data of channel
            channel_data = np.array([multiply(y, header_calibration) for y in data[i]])

            # Parse channel name
            channel_name = channel_tuple[0]

            # Get segments
            segments = [('0', header_epoch)]
            if config.has_section('SampleTimes'):
                segments = config.items('SampleTimes')

            unit = 'uV'

            # create channel
            channel = self.get_or_create_channel(
                name=channel_name.strip(),
                unit=unit,
                rate=header_rate,
                type='continuous')

            # Go through segments and write data to channel
            for j, segment in enumerate(segments):
                # Compute segment start and end times (see Note)
                segment_start_epoch = persyst.scaled(float(segment[1]))

                first_sample_for_segment = int(segment[0])

                first_sample_next_segment = num_samples if j == (
                        len(segments) - 1) else int(segments[j + 1][0])

                # get data segment
                segment_data = channel_data[first_sample_for_segment:first_sample_next_segment]

                timestamps = (1e6 * (np.arange(0, len(segment_data))/header_rate)) + segment_start_epoch

                self.LOGGER.debug('Header Rate: ' + str(header_rate) + ' Sampling rate: ' +
                                  str( 1000000/((timestamps[10]-timestamps[0])/10) ))
                self.LOGGER.debug('Length data: ' + str(len(segment_data)) + " Length timestamp: "
                                  + str(len(timestamps)))
                self.LOGGER.debug('Writing Segment: ' + str(j) + 'timestamp 1: '
                                  + str(timestamps[0])+", " + str(timestamps[1]))

                self.write_channel_data(
                    channel=channel,
                    timestamps=timestamps,
                    values=segment_data)

            self.finalize()

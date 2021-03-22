import numpy as np
import datetime
import struct

class NicoletFile(object):
    def __init__(self, fname):
        '''
        Descriptor goes here
        '''
        self.fname = fname

        #public properties
        self.patient_info  = None
        self.segments      = None
        self.event_markers = None

        self.N_seg  = None
        self.N_chan = None
        
        #private properties
        self._sections         = None
        self._index            = None
        self._sig_info         = None
        self._ts_info          = None
        self._ch_info          = None
        self._montage          = None
        self._Qi               = None
        self._all_index_ids    = None
        self._use_TS_info_indx = None

        #load the metadata
        self.load_metadata()

        self.N_seg = len(self.segments)
        tags         = [sec['tag'] for sec in self._sections] #list of all tags
        is_chan      = [tag.isdigit() for tag in tags]        #logical list of tags that are integers
        section_inds = [self._sections[i]['index'] for i in range(len(self._sections)) if is_chan[i]]
        self.N_chan = len(section_inds)

        
        
    def load_metadata(self):
        CONST = {
            'LABELSIZE'    : 32,
            'TSLABELSIZE'  : 64,
            'UNITSIZE'     : 16,
            'ITEMNAMESIZE' : 64,
        }

        f = open(self.fname,'rb')

        # misc
        #-----
        misc1     = np.fromfile(f, dtype='uint32', count=5)
        unknown   = np.fromfile(f, dtype='uint32', count=1)[0]
        index_idx = np.fromfile(f, dtype='uint32', count=1)[0]

        # Get tags and channel IDs
        #-------------------------
        f.seek(172,0) #Seek to 172 relative to beginning.
        n_tags = np.fromfile(f, dtype='uint32', count=1)[0]
        tags = []
        ID_lookup = {
            'ExtraDataTags'                          : 'ExtraDataTags',
            'SegmentStream'                          : 'SegmentStream',
            'DataStream'                             : 'DataStream',
            'InfoChangeStream'                       : 'InfoChangeStream',
            'InfoGuids'                              : 'InfoGuids',
            'Events'                                 : 'Events',
            '{A271CCCB-515D-4590-B6A1-DC170C8D6EE2}' : 'TSGUID',
            '{8A19AA48-BEA0-40D5-B89F-667FC578D635}' : 'DERIVATIONGUID',
            '{F824D60C-995E-4D94-9578-893C755ECB99}' : 'FILTERGUID',
            '{02950361-35BB-4A22-9F0B-C78AAA5DB094}' : 'DISPLAYGUID',
            '{8E94EF21-70F5-11D3-8F72-00105A9AFD56}' : 'FILEINFOGUID',
            '{E4138BC0-7733-11D3-8685-0050044DAAB1}' : 'SRINFOGUID',
            '{C728E565-E5A0-4419-93D2-F6CFC69F3B8F}' : 'EVENTTYPEINFOGUID',
            '{D01B34A0-9DBD-11D3-93D3-00500400C148}' : 'AUDIOINFOGUID',
            '{BF7C95EF-6C3B-4E70-9E11-779BFFF58EA7}' : 'CHANNELGUID',
            '{2DEB82A1-D15F-4770-A4A4-CF03815F52DE}' : 'INPUTGUID',
            '{5B036022-2EDC-465F-86EC-C0A4AB1A7A91}' : 'INPUTSETTINGSGUID',
            '{99A636F2-51F7-4B9D-9569-C7D45058431A}' : 'PHOTICGUID',
            '{55C5E044-5541-4594-9E35-5B3004EF7647}' : 'ERRORGUID',
            '{223A3CA0-B5AC-43FB-B0A8-74CF8752BDBE}' : 'VIDEOGUID',
            '{0623B545-38BE-4939-B9D0-55F5E241278D}' : 'DETECTIONPARAMSGUID',
            '{CE06297D-D9D6-4E4B-8EAC-305EA1243EAB}' : 'PAGEGUID',
            '{782B34E8-8E51-4BB9-9701-3227BB882A23}' : 'ACCINFOGUID',
            '{3A6E8546-D144-4B55-A2C7-40DF579ED11E}' : 'RECCTRLGUID',
            '{D046F2B0-5130-41B1-ABD7-38C12B32FAC3}' : 'GUID TRENDINFOGUID',
            '{CBEBA8E6-1CDA-4509-B6C2-6AC2EA7DB8F8}' : 'HWINFOGUID',
            '{E11C4CBA-0753-4655-A1E9-2B2309D1545B}' : 'VIDEOSYNCGUID',
            '{B9344241-7AC1-42B5-BE9B-B7AFA16CBFA5}' : 'SLEEPSCOREINFOGUID',
            '{15B41C32-0294-440E-ADFF-DD8B61C8B5AE}' : 'FOURIERSETTINGSGUID',
            '{024FA81F-6A83-43C8-8C82-241A5501F0A1}' : 'SPECTRUMGUID',
            '{8032E68A-EA3E-42E8-893E-6E93C59ED515}' : 'SIGNALINFOGUID',
            '{30950D98-C39C-4352-AF3E-CB17D5B93DED}' : 'SENSORINFOGUID',
            '{F5D39CD3-A340-4172-A1A3-78B2CDBCCB9F}' : 'DERIVEDSIGNALINFOGUID',
            '{969FBB89-EE8E-4501-AD40-FB5A448BC4F9}' : 'ARTIFACTINFOGUID',
            '{02948284-17EC-4538-A7FA-8E18BD65E167}' : 'STUDYINFOGUID',
            '{D0B3FD0B-49D9-4BF0-8929-296DE5A55910}' : 'PATIENTINFOGUID',
            '{7842FEF5-A686-459D-8196-769FC0AD99B3}' : 'DOCUMENTINFOGUID',
            '{BCDAEE87-2496-4DF4-B07C-8B4E31E3C495}' : 'USERSINFOGUID',
            '{B799F680-72A4-11D3-93D3-00500400C148}' : 'EVENTGUID',
            '{AF2B3281-7FCE-11D2-B2DE-00104B6FC652}' : 'SHORTSAMPLESGUID',
            '{89A091B3-972E-4DA2-9266-261B186302A9}' : 'DELAYLINESAMPLESGUID',
            '{291E2381-B3B4-44D1-BB77-8CF5C24420D7}' : 'GENERALSAMPLESGUID',
            '{5F11C628-FCCC-4FDD-B429-5EC94CB3AFEB}' : 'FILTERSAMPLESGUID',
            '{728087F8-73E1-44D1-8882-C770976478A2}' : 'DATEXDATAGUID',
            '{35F356D9-0F1C-4DFE-8286-D3DB3346FD75}' : 'TESTINFOGUID',
        }

        for i in range(n_tags):
            tags.append({})

            #tagID
            tags[i]['tag']   = np.fromfile(f, dtype='uint16', count=40) #actually reading 40 characters
            tags[i]['tag']   = ''.join([chr(c) for c in tags[i]['tag']])    #convert bytes to characters, make into string
            tags[i]['tag']   = tags[i]['tag'].strip('\x00')                 #remove spaces(?)
            #tag index
            tags[i]['index'] = np.fromfile(f, dtype='uint32', count=1)[0]
            #string rep of tagID
            if tags[i]['tag'].isdigit():
                tags[i]['IDStr'] = tags[i]['tag']
            else:
                tags[i]['IDStr'] = ID_lookup.get(tags[i]['tag'],'UNKNOWN') #get IDstr from tag_ID_dict

        self._sections = tags
                
        # QI Indexes
        #=================================================================================
        f.seek(172208,0)
        Qi = {
            'n_entries' : np.fromfile(f, dtype='uint32', count=1)[0],
            'misc1'     : np.fromfile(f, dtype='uint32', count=1)[0],
            'index_idx' : np.fromfile(f, dtype='uint32', count=1)[0],
            'misc3'     : np.fromfile(f, dtype='uint32', count=1)[0],
            'LQi'       : np.fromfile(f, dtype='uint64', count=1)[0],
            'first_idx' : np.fromfile(f, dtype='uint64', count=n_tags),
        }
        self._Qi = Qi

        index = []
        next_indx_loc = index_idx
        cur_indx = 0
        while cur_indx < Qi['n_entries']:
            f.seek(next_indx_loc,0)
            n_idx = np.fromfile(f, dtype='uint64', count=1)[0]
            var   = np.fromfile(f, dtype='uint64', count=int(3*n_idx))
            for j in range(n_idx):
                index.append({
                    'section_idx' : var[3*j + 0],
                    'offset'      : var[3*j + 1],
                    'block_L'     : int(var[3*j + 2] % 2**32),
                    'section_L'   : int(round(var[3*j + 2] / 2.**32)),
                })
            cur_indx += n_idx
            next_indx_loc = np.fromfile(f, dtype='uint64', count=1)[0]

        self._index = index
        self._all_index_ids = [ind['section_idx'] for ind in index]
        #---------------------------------------------------
            
        # Read dynamic packets
        #---------------------
        dynamic_packets = []

        tag_idx     = [tags[i]['IDStr'] for i in range(len(tags))].index('InfoChangeStream') #get index of tag with IDStr=='InfoChangeStream'
        section_idx = tags[tag_idx]['index'] #get section_idx from tag
        index_idx   = [index[i]['section_idx'] for i in range(len(index))].index(section_idx) #need to find index[] with 'section_idx' == section_idx

        offset = index[index_idx]['offset']
        n_dynamic_packets = index[index_idx]['section_L'] / 48
        f.seek(offset,0)

        # read structure first (no data)
        for i in range(n_dynamic_packets):
            guid_mixed           = np.fromfile(f, dtype='uint8', count=16)
            guid_unmixed         = guid_mixed[[3,2,1,0,5,4,7,6,8,9,10,11,12,13,14,15]]
            guid                 = ''.join(['{:02X}'.format(j) for j in guid_unmixed])
            guid_as_str          = '{{{}-{}-{}-{}-{}}}'.format(guid[0:8],guid[8:12],guid[12:16],guid[16:20],guid[20:])
            dynamic_packets.append({
                'offset'                : int(offset) + (i+1)*48, #think we need +1 here 'cuz matlab's dumb.
                'guid'                  : guid,
                'guid_as_str'           : guid_as_str,
                'date'                  : 693961 + np.fromfile(f, dtype='float64', count=1)[0], #693961=datenum(1899,12,31) in matlab
                'date_frac'             : np.fromfile(f, dtype='float64', count=1)[0],
                'internal_offset_start' : np.fromfile(f, dtype='uint64', count=1)[0],
                'packet_size'           : np.fromfile(f, dtype='uint64', count=1)[0],
                'data'                  : np.zeros(0,dtype='uint8'),
                'IDStr'                 : ID_lookup.get(guid_as_str,'UNKNOWN'), #get IDstr from ID_dict
            })

        # now read the actual data
        for i in range(n_dynamic_packets):
            # look for tag with same guid as dynamic_packet[i]
            tag_idx = [tags[j]['tag'] for j in range(len(tags))].index(dynamic_packets[i]['guid_as_str'])
            info_idx = tags[tag_idx]['index'] #SAME OFFSET AS ABOVE! THIS MAY BE A PROBLEM

            #get index with section_idx == info_idx
            section_idxs = np.array([index[j]['section_idx'] for j in range(len(index))]) #array of section_idxs from indexs
            index_idxs = np.where(section_idxs==info_idx)
            index_instances = [index[j] for j in index_idxs[0]]

            internal_offset = 0;
            remaining_data_to_read = dynamic_packets[i]['packet_size']
            current_target_start = dynamic_packets[i]['internal_offset_start']

            for j in range(len(index_instances)):
                if (internal_offset <= current_target_start) and (internal_offset+index_instances[j]['section_L'] >= current_target_start):

                    start  = current_target_start
                    stop   = min(start+remaining_data_to_read, internal_offset+index_instances[j]['section_L'])
                    n_read = int(stop - start)

                    f_start_pos = int(index_instances[j]['offset'] + start - internal_offset)
                    f.seek(f_start_pos,0)
                    data_part = np.fromfile(f, dtype='uint8', count=n_read)
                    dynamic_packets[i]['data'] = np.hstack((dynamic_packets[i]['data'],data_part))

                    remaining_data_to_read -= n_read
                    current_target_start += n_read

                internal_offset += index_instances[j]['section_L']

        # PATIENT INFO -- patient_info
        #========================================================================================
        info = {}
        info_keys = ['patientID', 'firstName', 'middleName', 'lastName', 'altID', 'mothersMaidenName', 'DOB', 'DOD', 'street', 'sexID', 'phone', 'notes', 'dominance', 'siteID', 'suffix', 'prefix', 'degree', 'apartment', 'city', 'state', 'country', 'language', 'height', 'weight', 'race', 'religion', 'maritalStatus']

        info_idx = tags[[tag['IDStr'] for tag in tags].index('PATIENTINFOGUID')]['index']
        index_instance = index[[ind['section_idx'] for ind in index].index(info_idx)]

        f.seek(index_instance['offset'],0)
        guid      = np.fromfile(f, dtype='uint8',  count=16)
        l_section = np.fromfile(f, dtype='uint64', count=1)[0]
        n_values  = np.fromfile(f, dtype='uint64', count=1)[0]
        n_Bstr    = int(np.fromfile(f, dtype='uint64', count=1)[0])

        segments = []
        for i in range(n_values):
            segments.append({
                'unix_time' : None,
            })

            key_ind = int(np.fromfile(f, dtype='uint64', count=1)[0])
            if key_ind in [7,8]:
                unix_time = np.fromfile(f, dtype='float64', count=1)[0] * 3600*24 - 2209161600
                #choosing to ignore dateStr for now, instead saving unix time
                date = (datetime.datetime.fromtimestamp(unix_time)+datetime.timedelta(hours=12)).date() #get rounded date
                value = [date.day, date.month, date.year]

            elif key_ind in [23,24]:
                value = np.fromfile(f, dtype='float64', count=1)[0]
            else:
                value = 0

            info[info_keys[key_ind-1]] = value


        str_setup = np.fromfile(f, dtype='uint64', count=n_Bstr*2)
        for i in range(0,n_Bstr*2,2):
            key_ind = int(str_setup[i])
            value = np.fromfile(f, dtype='uint16', count=int(str_setup[i+1]) + 1)
            value = ''.join([chr(c) for c in value])
            value = value.strip('\x00')
            info[info_keys[key_ind-1]] = value

        self.patient_info = info
        #-------------------------------------------
        
        # get INFOGUID
        #-------------
        info_idx = tags[[tag['IDStr'] for tag in tags].index('InfoGuids')]['index']
        index_instance = index[[ind['section_idx'] for ind in index].index(info_idx)]
        f.seek(index_instance['offset'],0)
        #ignoring, is list of GUIDS in file

        # SIGNAL INFO -- _sig_info
        #==========================================================================================
        info_idx = tags[[tag['IDStr'] for tag in tags].index('SIGNALINFOGUID')]['index']
        index_instance = index[[ind['section_idx'] for ind in index].index(info_idx)]
        f.seek(index_instance['offset'],0)

        SIG = {
            'guid' : np.fromfile(f, dtype='uint8', count=16),
            'name' : ''.join([chr(c) for c in np.fromfile(f, dtype='uint8', count=CONST['ITEMNAMESIZE'])]),
        }

        unknown = np.fromfile(f, dtype='int8', count=152) #ok<NASGU>
        f.seek(512,1)
        n_idx = np.fromfile(f, dtype='uint16', count=1)[0]
        misc1 = np.fromfile(f, dtype='uint16', count=3)

        sigInfo = []
        for i in range(n_idx):
            sigInfo.append({
                'sensorName'  : ''.join([chr(c) for c in np.fromfile(f, dtype='uint16', count=CONST['LABELSIZE'])]).strip('\x00'),
                'transducer'  : ''.join([chr(c) for c in np.fromfile(f, dtype='uint16', count=CONST['UNITSIZE'])]).strip('\x00'),
                'guid'        : np.fromfile(f, dtype='uint8',  count=16),
                'bBiPolar'    : bool(np.fromfile(f, dtype='uint32', count=1)[0]),
                'bAC'         : bool(np.fromfile(f, dtype='uint32', count=1)[0]),
                'bHighFilter' : bool(np.fromfile(f, dtype='uint32', count=1)[0]),
                'color'       : np.fromfile(f, dtype='uint32', count=1)[0],
            })
            reserved = np.fromfile(f, dtype='int8', count=256)

        self._sig_info = sigInfo
        #-------------------------------------------------
            
        # CHANNELINFO -- _ch_info
        #===========================================================================================
        info_idx = tags[[tag['IDStr'] for tag in tags].index('CHANNELGUID')]['index']
        index_instance = index[[ind['section_idx'] for ind in index].index(info_idx)]
        f.seek(index_instance['offset'],0)    

        CHAN = {
            'guid'     : np.fromfile(f, dtype='uint8', count=16),
            'name'     : ''.join([chr(c) for c in np.fromfile(f, dtype='uint8', count=CONST['ITEMNAMESIZE'])]),
        }
        f.seek(152,1)
        CHAN['reserved'] = np.fromfile(f, dtype='uint8', count=16)
        CHAN['deviceID'] = np.fromfile(f, dtype='uint8', count=16)
        f.seek(488,1)

        n_idx = np.fromfile(f, dtype='uint32', count=2)
        ch_info = []
        for i in range(n_idx[1]):
            ch_info.append({
                'sensor'          : ''.join([chr(c) for c in np.fromfile(f, dtype='uint16', count=CONST['LABELSIZE'])]).strip('\x00'),
                'samplingRate'    : np.fromfile(f, dtype='float64', count=1)[0],
                'bOn'             : np.fromfile(f, dtype='uint32', count=1)[0],
                'lInputID'        : np.fromfile(f, dtype='uint32', count=1)[0],
                'lInputSettingID' : np.fromfile(f, dtype='uint32', count=1)[0],
                'reserved'        : ''.join([chr(c) for c in np.fromfile(f, dtype='uint8', count=4)]),
            })
            f.seek(128,1)

        cur_idx = 0
        for i in range(len(ch_info)):
            if ch_info[i]['bOn']:
                ch_info[i]['indexID'] = cur_idx
                cur_idx += 1
            else:
                ch_info[i]['indexID'] = -1

        self._ch_info = ch_info
        #------------------------------------------
                
        # TS Info
        #=================================================================================================
        def uint8_cast(x,dtype):
            '''
            Converts a list of uint8's to the specified datatype

            Because, for some smart reason, we read the bytes in as uint8's first, and now we gotta convert them again
            '''
            #first, convert x to bytestring
            s = str(bytearray(x))
            #then, convert to desired datatype
            y = np.fromstring(s, dtype=dtype)
            if len(y) == 1: y=y[0]
            return y

        tsPacketIdxs = np.where([packet['IDStr']=='TSGUID' for packet in dynamic_packets])[0]
        tsPackets = [dynamic_packets[i] for i in tsPacketIdxs]

        if len(tsPackets) == 0:
            print('**WARNING**\nNo TSinfo found')
        else:
            if len(tsPackets) > 1:
                print('**WARNING**\nMultiple TSinfo packets detected; using first instance')

            tsPacket = tsPackets[0]
            ts_info = []

            #need to convert these lists of 4 uint8s to a single uint32
            elems = uint8_cast(tsPacket['data'][752:756], 'uint32')
            alloc = uint8_cast(tsPacket['data'][756:760], 'uint32')
            offset = 760 #761 I think we need to decrement this to avoid an off-by-one error. Cuz matlab

            for i in range(elems):
                i_offset = 0
                ts_info.append({})

                ts_info[i]['label']         = ''.join([chr(c) for c in uint8_cast(tsPacket['data'][offset:offset+CONST['TSLABELSIZE']], dtype='uint16')]).strip('\x00')
                i_offset                   += CONST['TSLABELSIZE']*2
                ts_info[i]['activeSensor']  = ''.join([chr(c) for c in uint8_cast(tsPacket['data'][offset+i_offset:offset+i_offset+CONST['TSLABELSIZE']], dtype='uint16')]).strip('\x00')
                i_offset                   += CONST['TSLABELSIZE']
                ts_info[i]['refSensor']     = ''.join([chr(c) for c in uint8_cast(tsPacket['data'][offset+i_offset:offset+i_offset+8], dtype='uint16')]).strip('\x00')
                i_offset                   += 64 #64 because we're skipping 56 bytes apparently
                ts_info[i]['dLowCut']       = uint8_cast(tsPacket['data'][offset+i_offset:offset+i_offset+8], dtype='float64')
                i_offset                   += 8
                ts_info[i]['dHighCut']      = uint8_cast(tsPacket['data'][offset+i_offset:offset+i_offset+8], dtype='float64')
                i_offset                   += 8
                ts_info[i]['dSamplingRate'] = uint8_cast(tsPacket['data'][offset+i_offset:offset+i_offset+8], dtype='float64')
                i_offset                   += 8
                ts_info[i]['dResolution']   = uint8_cast(tsPacket['data'][offset+i_offset:offset+i_offset+8], dtype='float64')
                i_offset                   += 8
                ts_info[i]['bMark']         = uint8_cast(tsPacket['data'][offset+i_offset:offset+i_offset+2], dtype='uint16')
                i_offset                   += 2
                ts_info[i]['bNotch']        = uint8_cast(tsPacket['data'][offset+i_offset:offset+i_offset+2], dtype='uint16')
                i_offset                   += 2
                ts_info[i]['dEegOffset']    = uint8_cast(tsPacket['data'][offset+i_offset:offset+i_offset+8], dtype='float64')
                offset += 552

        self._ts_info = ts_info
                
        # get segment start times
        #------------------------
        info_idx = tags[[tag['IDStr'] for tag in tags].index('SegmentStream')]['index']
        index_instance = index[[ind['section_idx'] for ind in index].index(info_idx)]
        f.seek(index_instance['offset'],0)

        n_seg = index_instance['section_L']/152
        segments = []

        for i in range(n_seg):
            dateOLE = np.fromfile(f, dtype='float64', count=1)[0]
            unix_time = dateOLE*(3600*24) - 2209161600
            date = datetime.datetime.fromtimestamp(unix_time)
            dateStr = str(date)
            startDate = [date.year, date.month, date.day]
            startTime = [date.hour, date.minute, date.second]
            f.seek(8,1)
            dur = np.fromfile(f, dtype='float64', count=1)[0]
            f.seek(128,1)

            segments.append({
                'datetime'  : date,
                'dateOLE'   : dateOLE,
                'dateStr'   : dateStr,
                'startDate' : startDate,
                'startTime' : startTime,
                'duration'  : dur,
            })

        # get n_values per segment and channel
        for i in range(n_seg):
            segments[i]['chName']       = [ts['label'] for ts in ts_info]
            segments[i]['refName']      = [ts['refSensor'] for ts in ts_info]
            segments[i]['samplingRate'] = [ts['dSamplingRate'] for ts in ts_info]
            segments[i]['scale']        = [ts['dResolution'] for ts in ts_info]

        self.segments = segments
            
        # get events
        #-----------
        info_idx = tags[[tag['IDStr'] for tag in tags].index('Events')]['index']
        index_instance = index[[ind['section_idx'] for ind in index].index(info_idx)]
        offset = index_instance['offset']
        f.seek(offset,0)

        ePktLen = 272    # Event packet length, see EVENTPACKET definition
        eMrkLen = 240    # Event marker length, see EVENTMARKER definition 
        evtPktGUID = np.array([128,246,153,183,164,114,211,17,147,211,0,80,4,0,193,72], dtype='uint8')
        HCEVENT_TAGS = {
            '{A5A95612-A7F8-11CF-831A-0800091B5BDA}' : 'Annotation',
            '{A5A95646-A7F8-11CF-831A-0800091B5BDA}' : 'Seizure',
            '{08784382-C765-11D3-90CE-00104B6F4F70}' : 'Format change',
            '{6FF394DA-D1B8-46DA-B78F-866C67CF02AF}' : 'Photic',
            '{481DFC97-013C-4BC5-A203-871B0375A519}' : 'Posthyperventilation',
            '{725798BF-CD1C-4909-B793-6C7864C27AB7}' : 'Review progress',
            '{96315D79-5C24-4A65-B334-E31A95088D55}' : 'Exam start',
            '{A5A95608-A7F8-11CF-831A-0800091B5BDA}' : 'Hyperventilation',
            '{A5A95617-A7F8-11CF-831A-0800091B5BDA}' : 'Impedance',
        }
        DAYSECS = 86400.0  # From nrvdate.h

        pkt_GUID = np.fromfile(f, dtype='uint8', count=16)
        pkt_len  = np.fromfile(f, dtype='uint64', count=1)[0]
        eventMarkers = []
        i = 0
        while np.array_equal(pkt_GUID, evtPktGUID):
            eventMarkers.append({})

            f.seek(8,1) #skip eventID, not used
            evtDate         = np.fromfile(f, dtype='float64', count=1)[0]
            evtDateFraction = np.fromfile(f, dtype='float64', count=1)[0]
            evtPOSIXTime    = evtDate*24*3600 + evtDateFraction - 2209161600
            evtDateTime     = datetime.datetime.fromtimestamp(evtPOSIXTime)
            evtDateStr      = str(evtDateTime)
            evtDur          = np.fromfile(f, dtype='float64', count=1)[0]
            f.seek(48,1)
            evtUser         = ''.join([chr(c) for c in np.fromfile(f, dtype='uint16', count=12)]).strip('\x00')
            evtTextLen      = np.fromfile(f, dtype='uint64', count=1)[0]
            evtGUID         = np.fromfile(f, dtype='uint8', count=16)
            GUID_order      = [4,3,2,1,6,5,8,7,9,10,11,12,13,14,15,16]
            evtGUID         = ''.join(['{:02X}'.format(evtGUID[j-1]) for j in GUID_order])
            evtGUID         = '{' + evtGUID[0:8] + '-' + evtGUID[8:12] + '-' + evtGUID[12:16] + '-' + evtGUID[16:20] + '-' + evtGUID[20:] + '}'
            f.seek(16,1)
            evtLabel        = ''.join([chr(c) for c in np.fromfile(f, dtype='uint16', count=32)]).strip('\x00')

            eventMarkers[i]['dateOLE']      = evtDate
            eventMarkers[i]['dateFraction'] = evtDateFraction
            eventMarkers[i]['dateStr']      = evtDateStr
            eventMarkers[i]['duration']     = evtDur
            eventMarkers[i]['user']         = evtUser
            eventMarkers[i]['GUID']         = evtGUID
            eventMarkers[i]['label']        = evtLabel
            eventMarkers[i]['IDStr']        = HCEVENT_TAGS.get(eventMarkers[i]['GUID'], 'UNKNOWN')

            offset += pkt_len
            f.seek(offset,0)
            pkt_GUID = np.fromfile(f, dtype='uint8', count=16)
            pkt_len  = np.fromfile(f, dtype='uint64', count=1)[0]
            i += 1

        self.event_markers = eventMarkers

        # MONTAGE -- _montage
        #===================================================================================
        info_idx = tags[[tag['IDStr'] for tag in tags].index('DERIVATIONGUID')]['index']
        index_instance = index[[ind['section_idx'] for ind in index].index(info_idx)]
        f.seek(index_instance['offset'],0)
        f.seek(40,1)

        mtgName = ''.join([chr(c) for c in np.fromfile(f, dtype='uint16', count=32)]).strip('\x00')
        f.seek(640,1)
        numDerivations = np.fromfile(f, dtype='uint32', count=2)

        montage = []
        for i in range(numDerivations[0]):
            montage.append({
                'derivationName' : ''.join([chr(c) for c in np.fromfile(f, dtype='uint16', count=64)]).strip('\x00'),
                'signalName_1'   : ''.join([chr(c) for c in np.fromfile(f, dtype='uint16', count=32)]).strip('\x00'),
                'signalName_2'   : ''.join([chr(c) for c in np.fromfile(f, dtype='uint16', count=32)]).strip('\x00'),
            })
            f.seek(264,1)

        #display properties
        info_idx = tags[[tag['IDStr'] for tag in tags].index('DISPLAYGUID')]['index']
        index_instance = index[[ind['section_idx'] for ind in index].index(info_idx)]
        f.seek(index_instance['offset'],0)
        f.seek(40,1)

        displayName = ''.join([chr(c) for c in np.fromfile(f, dtype='uint16', count=32)]).strip('\x00')
        f.seek(640,1)
        numTraces = np.fromfile(f, dtype='uint32', count=2)

        if numTraces[0] == numDerivations[0]:
            for i in range(numTraces[0]):
                f.seek(32,1)
                montage[i]['color'] = np.fromfile(f, dtype='uint32', count=1)[0]
                f.seek(132,1)
        else:
            print('Could not amtch montage derivations with display color table')

        self._montage = montage
        #--------------------------------------------
            
        f.close()

    def get_data(self):
        '''
        Get all data segments
        '''
        n_seg = len(self.segments)

        segments = [self.get_segment(i) for i in range(n_seg)]

        return segments
        
    def get_segment(self,segment):
        '''
        Get a single data segment
        '''
        f = open(self.fname,'rb')

        n_segs = len(self.segments)
        if segment >= n_segs:
            print('Segment must be less than N segments')
            return

        cumsum_segs = np.insert(np.array([seg['duration'] for seg in self.segments]).cumsum().astype(int),0,0)
        
        #Find all channels
        tags         = [sec['tag'] for sec in self._sections] #list of all tags
        is_chan      = [tag.isdigit() for tag in tags]        #logical list of tags that are integers
        section_inds = [self._sections[i]['index'] for i in range(len(self._sections)) if is_chan[i]]

        N_chan = len(section_inds) #number of channels
        channels = []
        
        #iterate over all channels
        for i in range(N_chan):    
            fs   = self.segments[segment]['samplingRate'][i]
            gain = self.segments[segment]['scale'][i]
            
            #find all sections
            sec_inds = np.where(np.array(self._all_index_ids) == section_inds[i])[0]
            sec_lens = [self._index[ind]['section_L']/2 for ind in sec_inds]
            cumsum_sec_lens = np.insert(np.array(sec_lens).cumsum().astype(int),0,0)
            
            n_start = cumsum_segs[segment] * fs
            seg_start = np.argmax(cumsum_sec_lens >= n_start)
            seg_end = np.argmax(cumsum_sec_lens >= fs*self.segments[segment]['duration'] + n_start)
            if seg_end == 0: seg_end = len(cumsum_sec_lens)

            data = np.zeros(int(self.segments[segment]['duration'] * fs))
            data_index = 0

            for j in range(seg_start,seg_end):
                index = self._index[sec_inds[j]]
                f.seek(index['offset'],0)
                n_read = int(index['section_L']/2)
                
                data[data_index:data_index+n_read] = np.fromfile(f, dtype='int16', count=n_read) * gain
                data_index += n_read

            tStart = self.segments[segment]['datetime']
            tEnd   = tStart + datetime.timedelta(seconds=self.segments[segment]['duration'])
            ch_name = self.segments[segment]['chName'][i]
                
            channel = {
                'fs'    : fs,
                'gain'  : gain,
                'data'  : data,
                'name'  : ch_name,
                'start' : tStart,
                'end'   : tEnd,
            }

            channels.append(channel)

        return channels

    def get_chan_seg(self,segment,chan):
        f = open(self.fname,'rb')

        #Ensure segment and chan are in range
        if not 0 <= segment < self.N_seg:
            print('Segment must be less than N segments')
            return
        if not 0 <= chan < self.N_chan:
            print('Chan must be less than N channels')
            return
        
        cumsum_segs = np.insert(np.array([seg['duration'] for seg in self.segments]).cumsum().astype(int),0,0)
        
        #Find all channels
        tags         = [sec['tag'] for sec in self._sections] #list of all tags
        is_chan      = [tag.isdigit() for tag in tags]        #logical list of tags that are integers
        section_inds = [self._sections[i]['index'] for i in range(len(self._sections)) if is_chan[i]]
        
        #grab channel
        #------------
        fs   = self.segments[segment]['samplingRate'][chan]
        gain = self.segments[segment]['scale'][chan]
            
        #find all sections
        sec_inds = np.where(np.array(self._all_index_ids) == section_inds[chan])[0]
        sec_lens = [self._index[ind]['section_L']/2 for ind in sec_inds]
        cumsum_sec_lens = np.insert(np.array(sec_lens).cumsum().astype(int),0,0)
            
        n_start = cumsum_segs[segment] * fs
        seg_start = np.argmax(cumsum_sec_lens >= n_start)
        seg_end = np.argmax(cumsum_sec_lens >= fs*self.segments[segment]['duration'] + n_start)
        if seg_end == 0: seg_end = len(cumsum_sec_lens)

        data = np.zeros(int(self.segments[segment]['duration'] * fs))
        data_index = 0

        for j in range(seg_start,seg_end):
            index = self._index[sec_inds[j]]
            f.seek(index['offset'],0)
            n_read = int(index['section_L']/2)
            
            data[data_index:data_index+n_read] = np.fromfile(f, dtype='int16', count=n_read) * gain
            data_index += n_read

        tStart = self.segments[segment]['datetime']
        tEnd   = tStart + datetime.timedelta(seconds=self.segments[segment]['duration'])
        ch_name = self.segments[segment]['chName'][chan]
                
        channel = {
            'fs'    : fs,
            'gain'  : gain,
            'data'  : data,
            'name'  : ch_name,
            'start' : tStart,
            'end'   : tEnd,
            'units' : 'uV',
        }

        return channel


    def __iter__(self):
        for seg in range(self.N_seg):
            for chan in range(self.N_chan):
                yield self.get_chan_seg(seg,chan)

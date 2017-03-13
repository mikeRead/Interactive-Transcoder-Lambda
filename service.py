# -*- coding: utf-8 -*-
from __future__ import print_function

import pdb
import json
import boto3
import time
import urllib
import urllib2
import logging
import os
import hiplogging
import fastly

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

logger.info('Loading function')

s3_client = boto3.client('s3')
transcoder_client = boto3.client('elastictranscoder')

hc_logger = logging.getLogger('hipchat')
hc_logger.setLevel(logging.DEBUG)
hc_logger.addHandler(logging.StreamHandler())



hc_logging_handler = hiplogging.HipChatHandler(os.environ.get('HIPCHAT_API_KEY'), 'Interactive Video Encoding Status')
hc_logging_handler.setLevel(logging.DEBUG)
hc_logger.addHandler(hc_logging_handler)

def build_output(file_prefix, file_suffix, file_extension, preset_id, thumbnail_pattern , has_artwork=False):
    a = {
        'Key': file_prefix + '_' + file_suffix + '.' + file_extension,
        'PresetId': preset_id,
        'ThumbnailPattern': thumbnail_pattern,
    }

    if has_artwork == True:
        b = {
            'AlbumArt': {
                'MergePolicy': 'Prepend',
                'Artwork': []
            }
        }

        return merge_dicts(a, b)
    else:
        return a


def merge_dicts(*dict_args):
    '''
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    '''
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result

def submit_job(pipline_id, output_prefix, input_key, outputs=[], metadata={}):
    logger.info("Submitting job...")
    input_params = {
        'Key': input_key,
        'FrameRate': 'auto',
        'Resolution': 'auto',
        'AspectRatio': 'auto',
        'Interlaced': 'auto',
        'Container': 'auto'
    }
    return transcoder_client.create_job(
        PipelineId=pipline_id,
        OutputKeyPrefix=output_prefix,
        Input=input_params,
        Outputs=outputs,
        UserMetadata=metadata)

def cleanup_old_outputs(prefix, outputs):
    for output in outputs:
        s3_client.delete_object(
            Bucket='lc-media-origin',
            Key=prefix + "/" + output['Key']
        )

def purge_cdn(domain, path):
    print("Purging cache for " + domain + path)
    fastly_client = fastly.API()
    fastly_client.authenticate_by_key(os.environ.get('FASTLY_API_KEY'))
    fastly_client.purge_url(domain, path)

def on_error(error, items):
    print("An error occurred:", error)

def find_prefix_from_key(key):
    keys = key.split('/')
    del keys[-1]

    prefix = "/".join(keys)
    return prefix

def encode_audio(key, file_prefix, folder_prefix, metadata):
    outputs = [
        build_output(file_prefix, 'alexa', 'mp3', '1479330665333-ehhuah', '', True),
        build_output(file_prefix, '128k', 'mp3', '1479330702611-yyxc97', '', True),
        build_output(file_prefix, '256k', 'mp3', '1479330725159-dycuue', '', True),
        build_output(file_prefix, '320k', 'mp3', '1479330748152-hkbc0x', '', True),
        build_output(file_prefix, '128k', 'mp4', '1479330977771-gz58x4', '', True),
        build_output(file_prefix, '256k', 'mp4', '1479330965547-ort7gq', '', True),
        build_output(file_prefix, '320k', 'mp4', '1479330944481-fqhh4q', '', True)
    ]

    logger.info("Cleaning up any older assets...")
    cleanup_old_outputs(folder_prefix, outputs)

    output_prefix = folder_prefix + "/"
    return submit_job('1477868119625-7ldpmm', output_prefix, key, outputs, metadata['attributes'])

def encode_video(key, file_prefix, folder_prefix, metadata):
    outputs = [
        build_output(file_prefix, 'alexa', 'mp3', '1479330665333-ehhuah', '', False),
        build_output(file_prefix, '128k', 'mp3', '1479330702611-yyxc97', '', False),
        build_output(file_prefix, '256k', 'mp3', '1479330725159-dycuue', '', False),
        build_output(file_prefix, '320k', 'mp3', '1479330748152-hkbc0x', '', False),
        build_output(file_prefix, '128k', 'mp4', '1479330977771-gz58x4', '', False),
        build_output(file_prefix, '256k', 'mp4', '1479330965547-ort7gq', '', False),
        build_output(file_prefix, '320k', 'mp4', '1479330944481-fqhh4q', '', False),
        build_output(file_prefix, '1080p', 'mp4', '1484941774976-kji5xi', file_prefix + '-{count}', False),
        build_output(file_prefix, '720p', 'mp4', '1471794534841-hu5xxk', '', False),
        build_output(file_prefix, '480p', 'mp4', '1471794724943-9r1vql', '', False),
        build_output(file_prefix, '360p', 'mp4', '1471794811175-t76ocy', '', False),
        build_output(file_prefix, '240p', 'mp4', '1471794869898-qkmeqz', '', False),
        build_output(file_prefix, '144p', 'mp4', '1471794934083-fp4g4o', '', False),
        build_output(file_prefix, 'audio', 'mp4', '1471795058994-3w6x37', '', False)
    ]

    logger.info("Cleaning up any older assets...")
    cleanup_old_outputs(folder_prefix, outputs)

    output_prefix = folder_prefix + "/"
    return submit_job('1477868119625-7ldpmm', output_prefix, key, outputs, metadata['attributes'])

def encode_podcast_video(key, file_prefix, folder_prefix, metadata):
    outputs = [
        build_output(file_prefix, '1080p', 'mp4', '1479750076994-izlzu9', '', False),
        build_output(file_prefix, '720p', 'mp4', '1471794534841-hu5xxk', '', False),
        build_output(file_prefix, '480p', 'mp4', '1471794724943-9r1vql', '', False),
        build_output(file_prefix, '360p', 'mp4', '1471794811175-t76ocy', '', False),
        build_output(file_prefix, '240p', 'mp4', '1471794869898-qkmeqz', '', False),
        build_output(file_prefix, '144p', 'mp4', '1471794934083-fp4g4o', '', False),
        build_output(file_prefix, 'audio', 'mp4', '1471795058994-3w6x37', '', False)
    ]

    logger.info("Cleaning up any older assets...")
    cleanup_old_outputs(folder_prefix, outputs)

    output_prefix = folder_prefix + "/"
    return submit_job('1477868119625-7ldpmm', output_prefix, key, outputs, metadata['attributes'])

def encode_podcast_audio(key, file_prefix, folder_prefix, metadata):
    outputs = [
        build_output(file_prefix, 'alexa', 'mp3', '1479330665333-ehhuah', '', True),
        build_output(file_prefix, '128k', 'mp3', '1479330702611-yyxc97', '', True),
        build_output(file_prefix, '256k', 'mp3', '1479330725159-dycuue', '', True),
        build_output(file_prefix, '320k', 'mp3', '1479330748152-hkbc0x', '', True),
        build_output(file_prefix, '128k', 'mp4', '1479330977771-gz58x4', '', True),
        build_output(file_prefix, '256k', 'mp4', '1479330965547-ort7gq', '', True),
        build_output(file_prefix, '320k', 'mp4', '1479330944481-fqhh4q', '', True)
    ]

    logger.info("Cleaning up any older assets...")
    cleanup_old_outputs(folder_prefix, outputs)

    output_prefix = folder_prefix + "/"
    return submit_job('1477868119625-7ldpmm', output_prefix, key, outputs, metadata['attributes'])

def sns_status_handler(event, context):
    message = event['Records'][0]['Sns']['Message']
    job = json.loads(message)
    prefix = job['outputKeyPrefix']
    duration = job['outputs'][0]['duration']
    metadata = job['userMetadata']

    if job['state'] == 'PROGRESSING':
        hc_logger.log(20, "Encoding job " + job['jobId'] + " for " + job['input']['key'] + " is now in progress...")
    elif job['state'] == 'COMPLETED':
        hc_logger.info("Encoding job " + job['jobId'] + " for " + job['input']['key'] + " is complete!")

        for output in job['outputs']:
            purge_cdn('d.life.church', '/' + prefix + output['key'])


        # Rename First Thumbnail
        new_thumbnail = s3_client.Object('lc-media-origin', prefix + metadata['file_prefix'] + '_thumbnail.jpg')
        new_thumbnail.copy_from(CopySource='lc-media-origin/' + prefix + metadata['file_prefix'] + '-00002.jpg')

        # if this is a message, we want to update release date via API
        if job['userMetadata'].has_key('message_id'):
            message_id = job['userMetadata']['message_id']
            url = 'https://api.life.church/v2/ets/release_message?key=' + os.environ.get('LC_API_KEY')
            #url = 'http://localhost:3000/v2/ets/release_message?key=' + os.environ.get('LC_API_KEY')
            data = urllib.urlencode({'message_id': message_id, 'duration': duration})

            try:
                resp = urllib2.urlopen(url=url, data=data)
            except urllib2.HTTPError as e:
                if e.code != 200 or e.code != 201:
                    hc_logger.warn('There was a problem while trying to release the message with ID ' + message_id + '. Please manually check http://api.lifechurch.tv/admin, to make sure the message is set to release at the correct time.')



    elif job['state'] == 'WARNING':
        hc_logger.warn('Encoding for ' + job['input']['key'] + 'produced the following warning: ' + job['messageDetails'])
    elif job['state'] == 'ERROR':
        hc_logger.fatal('There was an error while encoding ' + job['input']['key'] + ' with Job ID ' + job['jobId'] + '. Please contact the Interactive Team.')

def handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.unquote_plus(event['Records'][0]['s3']['object']['key'])
    try:
        logger.info("Using waiter to waiting for object to persist thru s3 service…")
        waiter = s3_client.get_waiter('object_exists')
        waiter.wait(Bucket=bucket, Key=key)

        prefix = find_prefix_from_key(key)
        logger.debug(prefix)
        metadata_key = prefix + '/metadata.json'

        logger.debug("Looking up metadata from " + metadata_key)
        metadata_object = s3_client.get_object(Bucket=bucket, Key=metadata_key)
        metadata = json.loads(metadata_object['Body'].read().decode('utf-8'))

        file_extension = os.path.splitext(key)[1][1:].strip().lower()

        file_prefix = metadata['attributes']['file_prefix']
        folder_prefix = metadata['attributes']['folder_prefix']

        if metadata['attributes']['series_type'] == 'worship':
            job = encode_audio(key, file_prefix, folder_prefix, metadata)
        elif metadata['attributes']['series_type'] == 'podcast':
            if file_extension == 'mp4' or file_extension == 'mov':
                job = encode_podcast_video(key, file_prefix, folder_prefix, metadata)
            elif file_extension == 'mp3':
                job = encode_podcast_audio(key, file_prefix, folder_prefix, metadata)

        else:
            job = encode_video(key, file_prefix, folder_prefix, metadata)

        hc_logger.info("Encoding job has been created for " + key + " with Job ID: " + job['Job']['Id'])

    except Exception as e:
        logger.debug(e)
        logger.debug('Error getting object {} from bucket {}. Make sure they exist '
              'and your bucket is in the same region as this '
              'function.'.format(key, bucket))
        raise e

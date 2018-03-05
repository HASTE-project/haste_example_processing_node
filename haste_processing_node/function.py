from harmonicPE.daemon import listen_for_tasks

from .haste_storage_client_cache import get_storage_client
from .image_analysis.image_analysis import extract_image_features
from .simulator_messages import split_data_from_simulator


# TODO: This will break on MACOSX (see HIO code for fix)
# import subprocess
# hostname = subprocess.getoutput('hostname')

def process_data(message_bytes):
    print('message received with length bytes: ' + str(len(message_bytes)), flush=True)

    metadata, image_bytes = split_data_from_simulator(message_bytes)

    extracted_features = extract_image_features(metadata, image_bytes)

    # TODO: rename to 'course_features' or 'features_level_0' ?
    metadata['extracted_features'] = extracted_features

    # metadata['containerID'] = hostname

    # Get a storage client for the cache, and use it to save the blob and all metadata:
    stream_id = metadata.pop('stream_id')  # Identifies the data in storage - across all processing nodes. Required.
    timestamp_cloud_edge = metadata.pop('timestamp')  # Required
    location = metadata.pop('location', None)  # Optional
    substream_id = metadata.pop('substream_id', None)  # Optional

    haste_storage_client = get_storage_client(stream_id)

    haste_storage_client.save(timestamp_cloud_edge,
                              location,
                              substream_id,
                              image_bytes,
                              metadata)

    print('saved to storage!', flush=True)


# TODO: add toy example with local image to run extraction locally.


if __name__ == '__main__':
    # Start the daemon to listen for tasks:
    listen_for_tasks(process_data)

# Automatic Video Transcoding Function

This is an AWS Lambda function that is triggered via S3 Events; specifically ObjectCreate.

## Workflow & Structure

Series and Messages are created in our backend, and once created a directory and corresponding metadata.json file is created in S3.

For example, if we have a series called Under God and the message is called Grace and Truth, this is the following structure...

We first create the folder for the series

`sermon/under-god`

We create a `promo` folder to hold series promo video

`sermon/under-god/promo`

We create a folder for the message, that holds the video assets for the particular message

`sermon/under-god/grace-and-truth`

What's great about this, is that it no longer matters what the incoming filename is called. We rely on a metadata file for what it needs to be called.

### Message metadata.json structure
```ruby
{
      type: 'message',
      version: '1',
      attributes: {
        series_id: 1,
        series_slug: 'under-god',
        message_id: 2,
        series_type: 'sermon',
        folder_prefix: 'sermon/under-god',
        file_prefix: 'grace-and-truth'
      }
    }
```

### Series metadata.json structure
```ruby
{
      type: 'series',
      version: '1',
      attributes: {
        series_id: 1
        series_type: 'sermon',
        folder_prefix: 'sermon/under-god',
        file_prefix: 'promo'
      }
    }
```

So once a file is uploaded into the bucket setup, it triggers this lambda function.
It will read the metadata.json file in the directory where you upload the media and then fires off the a preset list of jobs to ElasticTranscoder.

Once complete, it also receive signals from ElasticTranscoder, to update our CDN to purge any cache, and notifies a chat room staff can watch to get details on how the job is going.

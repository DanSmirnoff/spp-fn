import logging
import os
from abc import ABC, abstractmethod
from typing import Any

import boto3

from backend_fastapi.fastapi_service.settings.settings import settings, Settings

logger = logging.getLogger(__name__)

s3 = boto3.client(
    service_name='s3',
    endpoint_url='https://storage.yandexcloud.net'
)


class AbstractDataLoader(ABC):

    @abstractmethod
    def get_data(self, **kwargs) -> Any:
        pass

    @abstractmethod
    def upload_data(self, **kwargs) -> bool:
        pass


class DataLoader(AbstractDataLoader):

    def get_data(self, **kwargs) -> bytes:

        response = s3.get_object(Bucket=kwargs['bucket'], Key=kwargs['key'])
        data_bytes = response['Body'].read()
        return data_bytes

    def upload_data(self, **kwargs) -> bool:
        """
        kwargs:
            filename
            bucket-name
            key
        """
        s3.upload_file(kwargs['filename'], kwargs['bucket'], kwargs['key'])
        return True

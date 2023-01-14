# Maker Joey Whelan

from redis import Connection, from_url
from argparse import ArgumentParser
import pandas as pd
import random
import string
from enum import Enum
import sys

REDIS_URL: str = 'redis://localhost:6379'   # default Redis endpoint
FIELD_LEN: int = 20                         # Max length of synthetic Redis object fields
NUM_FIELDS: int = 10                        # Max number of fields in a synthetic Redis object
NUM_SYNTH: int = 0                        # Number of synthetic objects to generate
BATCH_SIZE: int = 1000                      # Number of keys to fetch per SCAN

class DATA_TYPE(Enum):
    HASH = 'hash'
    JSON = 'ReJSON-RL'
    STRING = 'string'

class Analyzer(object):
    def __init__(self, args):
        self.connection: Connection = from_url(args.url)
        self.num_synthetic = args.nsynth
        self.batch_size = args.batchsize

    def _random_obj(self) -> dict:
        """ Generates random dict object for synthetic Hash Set or JSON
            Returns
            -------
            Dict with a random number of string fields
        """   
        obj = {}
        for i in range(random.randint(1, NUM_FIELDS)):
            rand_str = ''.join(random.choice(string.ascii_letters) for j in range(random.randint(1, FIELD_LEN)))
            obj[f'field{i}'] = rand_str
        return obj

    def _generate_data(self) -> dict:
        """ Loads synthetic Hash Set, JSON and String objects into Redis.

            Returns
            -------
            Dict with counts of each object type generated
        """   
        pipe = self.connection.pipeline(transaction=False)
        results = dict.fromkeys([e.value for e in DATA_TYPE],0)

        for i in range(self.num_synthetic):
            match random.choice(list(DATA_TYPE)):
                case DATA_TYPE.HASH:
                    obj = self._random_obj()
                    pipe.hset(f'key:{i}', mapping=obj)
                    results[DATA_TYPE.HASH.value] += 1
                case DATA_TYPE.JSON:
                    obj = self._random_obj()
                    pipe.json().set(f'key:{i}', '$', obj)
                    results[DATA_TYPE.JSON.value] += 1
                case DATA_TYPE.STRING:
                    rand_str = ''.join(random.choice(string.ascii_letters) for j in range(random.randint(1, FIELD_LEN)))
                    pipe.set(f'key:{i}', rand_str)
                    results[DATA_TYPE.STRING.value] += 1
            sys.stdout.write(f'\rGenerated Keys: {results}')
            sys.stdout.flush()
        print('\n')
        pipe.execute()
        return results
   
    def analyze(self) -> None:
        """ Does a batch SCAN of a Redis DB.  Compiles key type counts and their memory usage
        """ 
        if self.num_synthetic:
            self._generate_data()
        
        results: dict = {}
        cursor = '0'
        fetched = 0
        while cursor != 0:
            cursor, keys = self.connection.scan(cursor=cursor, count=self.batch_size)
            for key in keys:
                dtype = str(self.connection.type(key), 'UTF-8')
                memory = self.connection.memory_usage(key)
                if not dtype in results:
                    results[dtype] = []
                results[dtype].append(memory)
            fetched += len(keys)
            sys.stdout.write(f'\rFetched {fetched} keys')
            sys.stdout.flush()
        print('\n')
        df = pd.DataFrame.from_dict(results, orient='index').T
        return df.describe()

if __name__ == '__main__':
    parser = ArgumentParser(description='Redis Data Analyzer')

    parser.add_argument('--url', required=False, type=str, default=REDIS_URL, help='Redis URL connect string')
    parser.add_argument('--batchsize', required=False, type=int, default=BATCH_SIZE, help='Number keys to be retrieved per SCAN execution')
    parser.add_argument('--nsynth', required=False, type=int, default=NUM_SYNTH, help='Number of synthetic Redis objects to be generated')
    args = parser.parse_args()

    analyzer = Analyzer(args)
    result = analyzer.analyze()
    print(f'{result.to_markdown()}')
    
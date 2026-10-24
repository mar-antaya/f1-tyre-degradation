import argparse
from data_io import fetch
if __name__=='__main__':
    p=argparse.ArgumentParser(description='Download observed COTA timing; never substitutes demo data.')
    p.add_argument('--year',type=int,default=2024);p.add_argument('--session',choices=['R','Q'],default='R');p.add_argument('--telemetry',action='store_true')
    a=p.parse_args();fetch(a.year,a.session,a.telemetry)

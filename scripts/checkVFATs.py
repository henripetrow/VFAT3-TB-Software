#!/bin/env python

def getChipIDs(fname, debug=False):
    from lxml import etree
    data = etree.parse(fname)
    result = [node.text.strip()
        for node in data.xpath("//PART/BARCODE")]
    if debug:
        print(result)
    return result


def makeQuery(chipIDs, debug=False):
    # vfatQuery = "' OR data.VFAT3_SER_NUM='".join(["0x{:x}".format(int(chip)) for chip in chipIDs] )
    vfatQuery = "' OR data.VFAT3_BARCODE='".join(chipIDs)
    vfatQuery = vfatQuery+"'"
    vfatQuery = "data.VFAT3_BARCODE='"+vfatQuery
    if debug:
        print(vfatQuery)
    return vfatQuery


def doQuery(args, vfatQuery):
    import cx_Oracle
    gemdb = '{:s}/{:s}@{:s}'.format(args.dbuser,args.dbpass,args.dbname)

    db    = cx_Oracle.connect(gemdb)
    cur   = db.cursor()

    ## get all columns
    colquery="select COLUMN_NAME from ALL_TAB_COLUMNS where TABLE_NAME='GEM_VFAT3_PROD_SUMMARY_V_RH'"
    cur.execute(colquery)
    columns = ",".join([ r[0] for r in cur])

    subquery = "select {:s},max(RUN_NUMBER) over (partition by VFAT3_BARCODE) as LATEST_RUN_NUMBER from CMS_GEM_MUON_VIEW.GEM_VFAT3_PROD_SUMMARY_V_RH".format(columns)
    query = "select * from ({:s}) data where RUN_NUMBER = LATEST_RUN_NUMBER and ({:s})".format(subquery,vfatQuery)
    if args.debug:
        print(subquery)
        print(query)
    cur.execute(query)
    results = [ r for r in cur ]
    if args.debug:
        print(query)
        print(len(results))
    return results


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='checkVFATs.py Usage:')
    parser.add_argument("dbname", type=str, help="Name of the DB to query", metavar="dbname")
    parser.add_argument("dbuser", type=str, help="DB username", metavar="dbuser")
    parser.add_argument("dbpass", type=str, help="DB password", metavar="dbpass")
    parser.add_argument("fname",  type=str, help="Filename containing list of VFATs to upload", metavar="fname")
    parser.add_argument("-d", "--debug",  action='store_true', help="debug")
    args = parser.parse_args()

    chipIDs = getChipIDs(args.fname, debug=args.debug)
    result  = doQuery(args,makeQuery(chipIDs, debug=args.debug))
    try:
        assert (len(result) == len(chipIDs))
        print("Length of VFATs uploaded ({:d}) matches those returned from DB ({:d})".format(len(result), len(chipIDs)))
    except AssertionError as e:
        print('Error!Unable to find exact match between uploaded VFATs and VFATs in the DB (%s,%s)' % (len(result), len(chipIDs)))

        print(len(result), len(chipIDs))
        print "Hybrids found from the database:"
        for r in result:
            print(r[1])
        import sys
        sys.exit('Error!Unable to find exact match between uploaded VFATs and VFATs in the DB (%s,%s)' % (
        len(result), len(chipIDs)))
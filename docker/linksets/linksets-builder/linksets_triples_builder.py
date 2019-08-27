import psycopg2 as pg
import os
database_url = os.getenv('DATABASE_URL')
mb_area_template = """\
mb:{mb_code_2016:s} a f: ;
 am2: [ dv: "{mb_area_m2:f}"^^dc: ; crs: albers: ] .
"""
cc_area_template = """\
cc:{hydroid:s} a f: ;
 am2: [ dv: "{cc_area_m2:f}"^^dc: ; crs: albers: ] .
"""
overlaps_template = """\
:i{intersection_iter:d} a f: ;
 am2: [ dv: "{i_area_m2:f}"^^dc: ; crs: albers: ] .
:mo{intersection_iter:d} s: mb:{mb_code_2016:s} ;
 p: c: ;
 o: :i{intersection_iter:d} ;
 i: l: ;
 m: _:mb16cc_p .
:co{intersection_iter:d} s: cc:{hydroid:s} ;
 p: c: ;
 o: :i{intersection_iter:d} ;
 i: l: ;
 m: _:mb16cc_p .
:to{intersection_iter:d} s: mb:{mb_code_2016:s} ;
 p: tso: ;
 o: cc:{hydroid:s};
 i: l: ;
 m: _:mb16cc_p .
"""
mb_sf_within_template = """\
:mw{within_iter:d} s: mb:{mb_code_2016:s} ;
 p: w: ;
 o: cc:{hydroid:s} ;
 i: l: ;
 m: _:mb16cc_p .
"""
mb_sf_contains_template = """\
:mc{within_iter:d} s: mb:{mb_code_2016:s} ;
 p: c: ;
 o: cc:{hydroid:s} ;
 i: l: ;
 m: _:mb16cc_p .
"""
def do_overlaps():
    con = pg.connect("host={} port=5432 dbname=mydb user=postgres password=password".format(database_url))
    cur = con.cursor("cur1")
    cur.execute("""\
    SELECT mb.mb_code_2016, cc.hydroid, mb.mb_area, cc.cc_area, mb.i_area, mb.is_overlaps, cc.is_overlaps, mb.is_within, cc.is_within 
    FROM public."mbintersectccareas_classify" as mb
    INNER JOIN public."ccintersectmbareas_classify" as cc on mb.mb_code_2016 = cc.mb_code_2016 and mb.hydroid = cc.hydroid
    WHERE (mb.is_overlaps or cc.is_overlaps) and (not mb.is_within) and (not cc.is_within);
    -- LIMIT 10;
    -- ORDER BY mb.mb_code_2016;
    """)
    c = 0
    intersection_iter = 0
    expressed_mb_areas = set()
    expressed_cc_areas = set()
    with open("overlaps_all.ttl", "w") as outfile:
        for record in cur:
            intersection_iter += 1
            c += 1
            mb_code_2016 = str(record[0])
            hydroid = str(record[1])
            mb_area_m2 = float(record[2])
            cc_area_m2 = float(record[3])
            i_area_m2  = float(record[4])
            mb_area_m2 = round((mb_area_m2 / 100.0), 7) * 100.0
            cc_area_m2 = round((cc_area_m2 / 100.0), 7) * 100.0
            i_area_m2  = round((i_area_m2  / 100.0), 7) * 100.0
            if mb_code_2016 not in expressed_mb_areas:
                mb_area_chunk = mb_area_template.format(mb_code_2016=mb_code_2016, mb_area_m2=mb_area_m2)
                outfile.write(mb_area_chunk)
                expressed_mb_areas.add(mb_code_2016)
            if hydroid not in expressed_cc_areas:
                cc_area_chunk = cc_area_template.format(hydroid=hydroid, cc_area_m2=cc_area_m2)
                outfile.write(cc_area_chunk)
                expressed_cc_areas.add(hydroid)
            next_chunk = overlaps_template.format(mb_code_2016=mb_code_2016, hydroid=hydroid, intersection_iter=intersection_iter, i_area_m2=i_area_m2)
            outfile.write(next_chunk)
def do_withins():
    con = pg.connect("host={} dbname=mydb user=postgres password=password".format(database_url))
    cur = con.cursor("cur2")
    cur.execute("""\
    SELECT mb.mb_code_2016, cc.hydroid, mb.is_within, cc.is_within
    FROM public."mbintersectccareas_classify" as mb
    INNER JOIN public."ccintersectmbareas_classify" as cc on mb.mb_code_2016 = cc.mb_code_2016 and mb.hydroid = cc.hydroid
    WHERE mb.is_within or cc.is_within;
    -- LIMIT 10;
    -- ORDER BY mb.mb_code_2016;
    """)
    c = 0
    within_iter = 0
    with open("within_all.ttl", "w") as outfile:
        for record in cur:
            c+=1
            within_iter += 1
            mb_code_2016 = str(record[0])
            hydroid = str(record[1])
            mb_is_within = bool(record[2])
            cc_is_within = bool(record[3])
            if mb_is_within:
                next_chunk = mb_sf_within_template.format(mb_code_2016=mb_code_2016, hydroid=hydroid, within_iter=within_iter)
            else:
                next_chunk = mb_sf_contains_template.format(mb_code_2016=mb_code_2016, hydroid=hydroid, within_iter=within_iter)
            outfile.write(next_chunk)
if __name__ == "__main__":
    do_withins()
    do_overlaps()
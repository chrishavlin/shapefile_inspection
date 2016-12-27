"""
inspect_shapefile.py

collection of classes and methods for inspecting a shapefile

Copyright (C) 2016  Chris Havlin, <https://chrishavlin.wordpress.com>
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
import shapefile
import xml.etree.cElementTree as ET
import numpy as np

"""
 IMPORT THE SHAPEFILE 
"""

class field_description(object):
      """
         class for inspecting a single field
      """
      def __init__(self,name):
          self.fieldname=name
      
      def get_field_type(self,sf):
          """ self -- the object
              sf -- the shapefile object of interest """

          # pull out the fields
          fld = sf.fields[1:]
          field_names = [field[0] for field in fld]
          nshapes=len(sf.shapes())

          # find the data type of the field
          self.field_type=None
          shapeid=0
          print 'searching for non-empty entry for', self.fieldname,'...'
          while not self.field_type and shapeid < nshapes-1:
                rec=sf.record(shapeid)[field_names.index(self.fieldname)]
                if rec:
                   self.field_type=str(type(rec)).split("'")[1]
                   print 'data type found:', self.field_type
                shapeid += 1
   
      def get_unique_rec_values(self,sf):
          """
          finds unique values of records
          """

          # pull out the fields
          fld = sf.fields[1:]
          field_names = [field[0] for field in fld]
          nshapes=len(sf.shapes())

          self.rec_vals=list()

          shape_id = 0
          print 'Finding unique record values for',self.fieldname
          for rec in sf.iterRecords():
              # pull out shape geometry and records
              shape_id += 1
              pct_comp=float(int(float(shape_id)/float(nshapes)*10000))/100.

              if rec[field_names.index(self.fieldname)] not in self.rec_vals:
                 print shape_id, 'of', nshapes, ' shapes (', pct_comp,'% )'
                 print "  new record value:",rec[field_names.index(self.fieldname)]
                 self.rec_vals.append(rec[field_names.index(self.fieldname)])
          print 'Completed field name inspection \n'
 
def create_xml_file(sf,savedir,basename):
    metadata = ET.Element("metadata")
    filename = ET.SubElement(metadata,"filename",name=basename)


    fld = sf.fields[1:]
    fields0 = [field[0] for field in fld]

    dtypes = list()
    attr_list = list()
    for fld in fields0:
        dtypes.append('')
        attr_list.append(list())


    shapeid=0
    nshapes=len(sf.shapes())
    pct_0 = -1
    for rec in sf.iterRecords():
        pct_comp=float(int(float(shapeid)/float(nshapes)*10000))/100.

        if np.remainder(int(pct_comp),10)==0 and int(pct_comp) != pct_0:
           pct_0=pct_comp
           print 'processing',shapeid, 'of', nshapes, ' shapes (', pct_comp,'% )'

        # remove the empty fieldnames
        b= rec[:]
        field_names=fields0[:]
        while b.count('')>0:
              ind=b.index('')
              field_names.pop(ind)
              b.pop(ind)

        # check if non-empty fields have a recorded data type, store it if not
        for fld in field_names:
            if dtypes[fields0.index(fld)]=='':
               dtypes[fields0.index(fld)]=str(type(b[field_names.index(fld)])).split("'")[1]
            
            if dtypes[fields0.index(fld)]=='str':
               atts = attr_list[fields0.index(fld)]
               if b[field_names.index(fld)] not in atts: 
                  atts.append(b[field_names.index(fld)])
            else: 
               atts = attr_list[fields0.index(fld)]
               if len(atts)==0: 
                  atts.append(b[field_names.index(fld)])
                  atts.append(b[field_names.index(fld)])
               else:
                  atts[0] = min(atts[0], b[field_names.index(fld)])
                  atts[1] = max(atts[1], b[field_names.index(fld)])
               
        shapeid+=1

    for field in fields0:
        attr = ET.SubElement(filename,"attr",name=field)
        ET.SubElement(attr, "attrtype",name="data type").text = dtypes[fields0.index(field)]

        atts = attr_list[fields0.index(field)]
        attsamp_lab='unique str values'
        if len(atts)>40:
           attprint=str(atts[0:30]).replace("'","")
           attsamp_lab='sample of str values'
        elif dtypes[fields0.index(field)]!= 'str':
           attprint=str(atts[:]).replace("'","")
           attsamp_lab='min/max'
        else:
           attprint=str(atts[:]).replace("'","")
           attsamp_lab='unique str values'

        ET.SubElement(attr, "attrvals",name=attsamp_lab).text = attprint
    
    tree = ET.ElementTree(metadata)
    tree.write(savedir+basename+"_auto.xml")

if __name__ == '__main__':

   # set the shapefile
   shp_file_base='ex_QMDJXT8DzmqNh6eFiNkAuESyDNCX_osm_line'
   dat_dir='../../learning_shapefiles/shapefiles/denver_maps/grouped_by_geometry_type/'

   user_path=raw_input("Do you want to enter the path to a shapefile? (Y/N) ")
   print ' '
   if user_path=="Y":
      dat_dir=raw_input("Enter data directory (e.g., ../shapefiles/blah/): ")
      shp_file_base=raw_input("Enter shapefile file name (without extension): ")
   else:
      print 'Using shapefile specified in __main__ :'
      print 'directory: ',dat_dir
      print 'filename: ',shp_file_base
      
   # load the shapefile
   print '\n Loading shapefile ...'
   sf = shapefile.Reader(dat_dir+shp_file_base)
   print '... shapefile loaded! \n'

   # pull out the fields
   fld = sf.fields[1:]
   field_names = [field[0] for field in fld]
   print 'Shapefile has the following field names'
   print field_names,'\n'

   to_do=raw_input("Do you want to investigate single field (single)? Generate xml file (xml)? Or both (both)? ")

   if to_do == 'single' or to_do == 'both':
      field_of_interest=raw_input("Enter field name to investigate: ")
   
      # process the shapefile
      field_obj=field_description(field_of_interest) # store field name 
      field_obj.get_field_type(sf) # find field data type
      field_obj.get_unique_rec_values(sf) # find unique values
   
      print '---------------------------------------'
      print 'Shapefile has the following field names'
      print field_names
      print '\n The field name',field_obj.fieldname,' is ',field_obj.field_type
      print 'and has',len(field_obj.rec_vals),'unique values'
   
      Y_N=raw_input("Display Values? (Y/N) ")
      if Y_N=='Y':
         print ' possible values:'
         print field_obj.rec_vals

   if to_do == 'xml' or to_do == 'both':
      print '\nBuilding xml file...'
      create_xml_file(sf,dat_dir,shp_file_base)
      print '... Finished building xml file!'


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
          print 'searching for non-empty entry...'
          while not self.field_type and shapeid < nshapes-1:
                rec=sf.record(shapeid)[field_names.index(self.fieldname)]
                if rec:
                   self.field_type=type(rec) 
                   print 'data type found'
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
 
def create_xml_file(sf,savedir,basename):
    metadata = ET.Element("metadata")
    eainfo = ET.SubElement(metadata, "eainfo")
    detailed = ET.SubElement(eainfo,"detailed",name=basename)
    attr = ET.SubElement(detailed,"attr")
    
    ET.SubElement(attr, "attrlbl").text = "label"
    ET.SubElement(attr, "attrtype").text = "type"
    # if string with small number of types
    ET.SubElement(attr, "attrrange").text = "range"
    # if a number, just use min/max 
    
    tree = ET.ElementTree(metadata)
    tree.write(savedir+basename+"_auto.xml")

if __name__ == '__main__':

   # set the shapefile
   shp_file_base='ex_QMDJXT8DzmqNh6eFiNkAuESyDNCX_osm_line'
   dat_dir='../shapefiles/denver_maps/grouped_by_geometry_type/'

   user_path=raw_input("Do you want to enter the path to a shapefile? (Y/N) ")
   print ' '
   if user_path=="Y":
      dat_dir=raw_input("Enter data directory (e.g., ../shapefiles/blah/): ")
      shp_file_base=raw_input("Enter shapefile file name (without extension): ")
   else:
      print 'Using shapefile specified in __main__ :'
      print 'directory: ',dat_dir
      print 'filename: ',shp_file_base
      

   #shp_file_base='denver_tree_canopy_2013'
   #dat_dir='../shapefiles/denver_tree_canopy_2013/'

   # load the shapefile
   print ' '
   print 'Loading shapefile ...'
   sf = shapefile.Reader(dat_dir+shp_file_base)
   print '... shapefile loaded!'
   print ' '

   # pull out the fields
   fld = sf.fields[1:]
   field_names = [field[0] for field in fld]
   print 'Shapefile has the following field names'
   print field_names
   print ' '
   field_of_interest=raw_input("Enter field name to investigate: ")
   print ' '

   # process the shapefile
   field_obj=field_description(field_of_interest) # store field name 
   field_obj.get_field_type(sf) # find field data type
   field_obj.get_unique_rec_values(sf) # find unique values

   print '---------------------------------------'
   print 'Shapefile has the following field names'
   print field_names
   print ' '
   print 'The field name',field_obj.fieldname,' is ',field_obj.field_type
   print 'and has',len(field_obj.rec_vals),'unique values'

   Y_N=raw_input("Display Values? (Y/N) ")
   if Y_N=='Y':
      print ' possible values:'
      print field_obj.rec_vals

   if raw_input("Create XML file? (Y/N) ")=='Y':
      create_xml_file(sf,dat_dir,shp_file_base)


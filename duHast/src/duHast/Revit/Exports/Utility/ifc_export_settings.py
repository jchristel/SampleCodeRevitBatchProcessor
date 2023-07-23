"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
IFC export settings class.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright © 2023, Jan Christel
# All rights reserved.

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

# - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# - Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#
# This software is provided by the copyright holder "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed. 
# In no event shall the copyright holder be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits; 
# or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
#
#
#

import System
from duHast.Utilities.Objects import base


class IFCSettings(base.Base):

    supported_ifc_versions = {
        "Default": "The Autodesk Revit applications default export format. Note that this may change as the defaults change in the Revit user interface.",
        "IFCBCA": "IFC BCA file format. This is a certified variant of IFC 2x2 used for submitting files to the Singapore BCA ePlan Check Server.",
        "IFC2x2": "IFC 2x2 file format.",
        "IFC2x3": "IFC 2x3 file format.",
        "IFCCOBIE": "IFC GSA COBIE 2010 file format. This is a variant of IFC 2x3 used for submitting files that are COBIE 2010-complaint.",
        "IFC2x3CV2": "IFC 2x3 Coordination View 2.0 file format. This is a variant of IFC 2x3 used for exporting files using the Coordination View 2.0 model view.",
        "IFC4": "IFC 4 file format.",
        "IFC2x3FM": "IFC2x3 Extended FM Handover View",
        "IFC4RV": "IFC4 Reference View",
        "IFC4DTV": "IFC4 Design Transfer View",
        "IFC2x3BFM": "IFC2x3 Basic FM Handover View",
    }

    site_placement_options = {
        "SiteTransformBasis.Shared": "shared",
        "SiteTransformBasis.Site": "site",
        "SiteTransformBasis.Project": "project",
        "SiteTransformBasis.Internal": "internal",
        "SiteTransformBasis.ProjectInTN": "projectInTN",
        "SiteTransformBasis.InternalInTN": "internalInTN",
    }

    def __init__(
        self,
        name,
        ifc_version,
        space_boundaries,
        active_phase_id,
        active_view_id,
        export_base_quantities,
        split_walls_and_columns,
        visible_elements_of_current_view,
        use2_d_room_boundary_for_volume,
        use_family_and_type_name_for_reference,
        export_internal_revit_property_sets,
        export_ifc_common_property_sets,
        export_2d_elements,
        export_parts_as_building_elements,
        export_bounding_box,
        export_solid_model_rep,
        export_schedules_as_psets,
        export_user_defined_psets,
        export_user_defined_psets_file_name,
        export_linked_files,
        include_site_elevation,
        use_active_view_geometry,
        export_specific_schedules,
        tessellation_level_of_detail,
        store_ifc_guid,
        export_rooms_in_view,
        use_only_triangulation,
        include_steel_elements,
        cobie_company_info,
        cobie_project_info,
        use_type_name_only_for_ifc_type,
        use_visible_revit_name_as_entity_name,
        site_placement,
        selected_site,
        geo_ref_crs_name,
        geo_ref_crs_desc,
        geo_ref_epsg_code,
        geo_ref_geodetic_datum,
        geo_ref_map_unit,
        exclude_filter,
    ):

        """
        _summary_

        :param name: The name of the configuration.
        :type name:
        :param ifcVersion: The IFCFileFormat of the configuration.
        :type ifcVersion:
        :param spaceBoundaries: The level of space boundaries of the configuration.
        :type spaceBoundaries:
        :param activePhaseId: The phase of the document to export.
        :type activePhaseId:
        :param exportBaseQuantities: Whether or not to include base quantities for model elements in the export data. Base quantities are generated from model geometry to reflect actual physical quantity values, independent of measurement rules or methods.
        :type exportBaseQuantities:
        :param splitWallsAndColumns: Whether or not to split walls and columns by building stories.
        :type splitWallsAndColumns:
        :param visibleElementsOfCurrentView: True to export only the visible elements of the current view (based on filtering and/or element and category hiding). False to export the entire model.
        :type visibleElementsOfCurrentView:
        :param use2DRoomBoundaryForVolume: True to use a simplified approach to calculation of room volumes (based on extrusion of 2D room boundaries) which is also the default when exporting to IFC 2x2. False to use the Revit calculated room geometry to represent the room volumes (which is the default when exporting to IFC 2x3).
        :type use2DRoomBoundaryForVolume:
        :param useFamilyAndTypeNameForReference: True to use the family and type name for references. False to use the type name only.
        :type useFamilyAndTypeNameForReference:
        :param exportInternalRevitPropertySets: True to include the Revit-specific property sets based on parameter groups. False to exclude them.
        :type exportInternalRevitPropertySets:
        :param exportIFCCommonPropertySets: True to include the IFC common property sets. False to exclude them.
        :type exportIFCCommonPropertySets:
        :param export2DElements: True to include 2D elements supported by IFC export (notes and filled regions). False to exclude them.
        :type export2DElements:
        :param exportPartsAsBuildingElements: True to export the parts as independent building elements. False to export the parts with host element.
        :type exportPartsAsBuildingElements:
        :param exportBoundingBox: True to export bounding box. False to exclude them.
        :type exportBoundingBox:
        :param exportSolidModelRep: True to allow exports of solid models when possible. False to exclude them.
        :type exportSolidModelRep:
        :param exportSchedulesAsPsets: True to allow exports of schedules as custom property sets. False to exclude them.
        :type exportSchedulesAsPsets:
        :param exportUserDefinedPsets: True to allow user defined property sets to be exported. False to ignore them
        :type exportUserDefinedPsets:
        :param exportUserDefinedPsetsFileName: The name of the file containing the user defined Parameter Mapping Table to be exported.
        :type exportUserDefinedPsetsFileName:
        :param exportLinkedFiles: True to include links in export, otherwise False.
        :type exportLinkedFiles:
        :param includeSiteElevation: True to include IFCSITE elevation in the site local placement origin.
        :type includeSiteElevation:
        :param useActiveViewGeometry: True to use the active view when generating geometry. False to use default export options.
        :type useActiveViewGeometry:
        :param exportSpecificSchedules: True to export specific schedules
        :type exportSpecificSchedules:
        :param tessellationLevelOfDetail: Value indicating the level of detail to be used by tessellation. Valid values is between 0 to 1
        :type tessellationLevelOfDetail:
        :param storeIFCGUID: True to store the IFC GUID in the file after the export.  This will require manually saving the file to keep the parameter.
        :type storeIFCGUID:
        :param exportRoomsInView: True to export rooms if their bounding box intersect with the section box. If the section box isn't visible, then all the rooms are exported if this option is set.
        :type exportRoomsInView:
        :param useOnlyTriangulation: Value indicating whether tessellated geometry should be kept only as triangulation. (Note: in IFC4_ADD2 IfcPolygonalFaceSet is introduced that can simplify the coplanar triangle faces into a polygonal face. This option skip this)
        :type useOnlyTriangulation:
        :param includeSteelElements: Value indicating whether steel elements should be exported.
        :type includeSteelElements:
        :param cOBieCompanyInfo: COBie specific company information (from a dedicated tab)
        :type cOBieCompanyInfo:
        :param cOBieProjectInfo: COBie specific project information (from a dedicated tab)
        :type cOBieProjectInfo:
        :param activeViewId: Id of the active view.
        :type activeViewId: int
        :param useTypeNameOnlyForIfcType: Value indicating whether only the Type name will be used to name the IfcTypeObject
        :type useTypeNameOnlyForIfcType: bool
        :param useVisibleRevitNameAsEntityName: Value indicating whether the IFC Entity Name will use visible Revit Name
        :type useVisibleRevitNameAsEntityName: bool
        :param selectedSite: Selected Site name
        :type selectedSite: str
        :param sitePlacement: The origin of the exported file: either shared coordinates (Site Survey Point), Project Base Point, or internal coordinates.
        :type sitePlacement: str: SiteTransformBasis.Shared, SiteTransformBasis.Site, SiteTransformBasis.Project, SiteTransformBasis.Internal, SiteTransformBasis.ProjectInTN, SiteTransformBasis.InternalInTN
        :param geoRefCRSName: Projected Coordinate System Name
        :type geoRefCRSName: str
        :param geoRefCRSDesc: Projected Coordinate System Description
        :type geoRefCRSDesc: str
        :param geoRefEPSGCode: EPSG Code for the Projected CRS
        :type geoRefEPSGCode: str
        :param geoRefGeodeticDatum: The geodetic datum of the ProjectedCRS
        :type geoRefGeodeticDatum: str
        :param geoRefMapUnit: The Map Unit of the ProjectedCRS
        :type geoRefMapUnit: str
        :param excludeFilter: Exclude filter string (element list in an array, separated with semicolon ';')
        :type excludeFilter: str

        :raises Exception: _description_
        """

        # forwards all unused arguments
        # ini super class to allow multi inheritance in children!
        super(IFCSettings, self).__init__()

        self.name = name

        # check the IFC version
        if ifc_version in self.supported_ifc_versions:
            self.ifc_version = ifc_version
        else:
            raise Exception("Unsupported IFC version:" + ifc_version)

        self.space_boundaries = space_boundaries
        self.active_phase_id = active_phase_id
        self.active_view_id = active_view_id
        self.export_base_quantities = export_base_quantities
        self.split_walls_and_columns = split_walls_and_columns
        self.visible_elements_of_current_view = visible_elements_of_current_view
        self.use2_d_room_boundary_for_volume = use2_d_room_boundary_for_volume
        self.use_family_and_type_name_for_reference = (
            use_family_and_type_name_for_reference
        )
        self.export_internal_revit_property_sets = export_internal_revit_property_sets
        self.export_ifc_common_property_sets = export_ifc_common_property_sets
        self.export_2d_elements = export_2d_elements
        self.export_parts_as_building_elements = export_parts_as_building_elements
        self.export_bounding_box = export_bounding_box
        self.export_solid_model_rep = export_solid_model_rep
        self.export_schedules_as_psets = export_schedules_as_psets
        self.export_user_defined_psets = export_user_defined_psets
        self.export_user_defined_psets_file_name = export_user_defined_psets_file_name
        self.export_linked_files = export_linked_files
        self.include_site_elevation = include_site_elevation
        self.use_active_view_geometry = use_active_view_geometry
        self.export_specific_schedules = export_specific_schedules
        self.tessellation_level_of_detail = tessellation_level_of_detail
        self.store_ifc_guid = store_ifc_guid
        self.export_rooms_in_view = export_rooms_in_view
        self.use_only_triangulation = use_only_triangulation
        self.include_steel_elements = include_steel_elements
        self.cobie_company_info = cobie_company_info
        self.cobie_project_info = cobie_project_info
        self.use_type_name_only_for_ifc_type = (use_type_name_only_for_ifc_type,)
        self.use_visible_revit_name_as_entity_name = (
            use_visible_revit_name_as_entity_name
        )

        # check site placement option
        if site_placement in self.site_placement_options:
            self.site_placement = self.site_placement_options[site_placement]
        else:
            raise Exception("Unsupported site placement option:" + site_placement)

        self.selected_site = selected_site
        self.geo_ref_crs_name = geo_ref_crs_name
        self.geo_ref_crs_desc = geo_ref_crs_desc
        self.geo_ref_epsg_code = geo_ref_epsg_code
        self.geo_ref_geodetic_datum = geo_ref_geodetic_datum
        self.geo_ref_map_unit = geo_ref_map_unit
        self.exclude_filter = exclude_filter

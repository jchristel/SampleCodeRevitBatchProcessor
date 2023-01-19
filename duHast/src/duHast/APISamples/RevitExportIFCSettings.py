'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
IFC export settings class.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

#
#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2022  Jan Christel
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

import System

class IFCSettings():
    
    supportedIfcVersions = {
            'Default' : 'The Autodesk Revit applications default export format. Note that this may change as the defaults change in the Revit user interface.',
            'IFCBCA' : 'IFC BCA file format. This is a certified variant of IFC 2x2 used for submitting files to the Singapore BCA ePlan Check Server.',
            'IFC2x2' : 'IFC 2x2 file format.',
            'IFC2x3' : 'IFC 2x3 file format.',
            'IFCCOBIE' : 'IFC GSA COBIE 2010 file format. This is a variant of IFC 2x3 used for submitting files that are COBIE 2010-complaint.',
            'IFC2x3CV2' : 'IFC 2x3 Coordination View 2.0 file format. This is a variant of IFC 2x3 used for exporting files using the Coordination View 2.0 model view.',
            'IFC4' : 'IFC 4 file format.',
            'IFC2x3FM' : 'IFC2x3 Extended FM Handover View',
            'IFC4RV' : 'IFC4 Reference View',
            'IFC4DTV' : 'IFC4 Design Transfer View',
            'IFC2x3BFM' : 'IFC2x3 Basic FM Handover View'
        }
    
    sitePlacementOptions = {
        'SiteTransformBasis.Shared' :'shared', 
        'SiteTransformBasis.Site' : 'site', 
        'SiteTransformBasis.Project' : 'project',
        'SiteTransformBasis.Internal' : 'internal', 
        'SiteTransformBasis.ProjectInTN' : 'projectInTN',
        'SiteTransformBasis.InternalInTN' : 'internalInTN'
    }

    def __init__(
        self, 
        name, 
        ifcVersion, 
        spaceBoundaries,
        activePhaseId,
        activeViewId,
        exportBaseQuantities,
        splitWallsAndColumns,
        visibleElementsOfCurrentView,
        use2DRoomBoundaryForVolume,
        useFamilyAndTypeNameForReference,
        exportInternalRevitPropertySets,
        exportIFCCommonPropertySets,
        export2DElements,
        exportPartsAsBuildingElements,
        exportBoundingBox,
        exportSolidModelRep,
        exportSchedulesAsPsets,
        exportUserDefinedPsets,
        exportUserDefinedPsetsFileName,
        exportLinkedFiles,
        includeSiteElevation,
        useActiveViewGeometry,
        exportSpecificSchedules,
        tessellationLevelOfDetail,
        storeIFCGUID,
        exportRoomsInView,
        useOnlyTriangulation,
        includeSteelElements,
        cOBieCompanyInfo,
        cOBieProjectInfo,
        useTypeNameOnlyForIfcType,
        useVisibleRevitNameAsEntityName,
        sitePlacement,
        selectedSite,
        geoRefCRSName,
        geoRefCRSDesc,
        geoRefEPSGCode,
        geoRefGeodeticDatum,
        geoRefMapUnit,
        excludeFilter
        ):

        '''
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
        '''

        self.name = name

        # check the IFC version
        if(ifcVersion in self.supportedIfcVersions):
            self.ifcVersion = ifcVersion
        else:
            raise Exception('Unsupported IFC version:' + ifcVersion)

        self.spaceBoundaries = spaceBoundaries
        self.activePhaseId = activePhaseId
        self.activeViewId = activeViewId
        self.exportBaseQuantities = exportBaseQuantities
        self.splitWallsAndColumns = splitWallsAndColumns
        self.visibleElementsOfCurrentView = visibleElementsOfCurrentView
        self.use2DRoomBoundaryForVolume = use2DRoomBoundaryForVolume
        self.useFamilyAndTypeNameForReference = useFamilyAndTypeNameForReference
        self.exportInternalRevitPropertySets = exportInternalRevitPropertySets
        self.exportIFCCommonPropertySets = exportIFCCommonPropertySets
        self.export2DElements = export2DElements
        self.exportPartsAsBuildingElements = exportPartsAsBuildingElements
        self.exportBoundingBox = exportBoundingBox
        self.exportSolidModelRep = exportSolidModelRep
        self.exportSchedulesAsPsets = exportSchedulesAsPsets
        self.exportUserDefinedPsets = exportUserDefinedPsets
        self.exportUserDefinedPsetsFileName = exportUserDefinedPsetsFileName
        self.exportLinkedFiles = exportLinkedFiles
        self.includeSiteElevation = includeSiteElevation
        self.useActiveViewGeometry = useActiveViewGeometry
        self.exportSpecificSchedules = exportSpecificSchedules
        self.tessellationLevelOfDetail = tessellationLevelOfDetail
        self.storeIFCGUID = storeIFCGUID
        self.exportRoomsInView = exportRoomsInView
        self.useOnlyTriangulation = useOnlyTriangulation
        self.includeSteelElements = includeSteelElements
        self.cOBieCompanyInfo = cOBieCompanyInfo
        self.cOBieProjectInfo = cOBieProjectInfo
        self.useTypeNameOnlyForIfcType = useTypeNameOnlyForIfcType,
        self.useVisibleRevitNameAsEntityName = useVisibleRevitNameAsEntityName
        
        # check site placement option
        if(sitePlacement in self.sitePlacementOptions):
            self.sitePlacement =  self.sitePlacementOptions[sitePlacement]
        else:
            raise Exception('Unsupported site placement option:' + sitePlacement)
        
        self.selectedSite = selectedSite
        self.geoRefCRSName = geoRefCRSName
        self.geoRefCRSDesc = geoRefCRSDesc
        self.geoRefEPSGCode = geoRefEPSGCode
        self.geoRefGeodeticDatum = geoRefGeodeticDatum
        self.geoRefMapUnit = geoRefMapUnit
        self.excludeFilter = excludeFilter
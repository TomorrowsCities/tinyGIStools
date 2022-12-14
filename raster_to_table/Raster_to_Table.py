"""
Model exported as python.
Name : Raster to Points with X/Y Coordinates
Group : 
With QGIS : 32206
by: Emin Yahya Menteşe
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterRasterLayer
from qgis.core import QgsProcessingParameterFileDestination
from qgis.core import QgsCoordinateReferenceSystem
import processing


class RasterToPointsWithXyCoordinates(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterRasterLayer('InputRaster', 'Input Raster', defaultValue=None))
        self.addParameter(QgsProcessingParameterFileDestination('Spreadsheet_output', 'spreadsheet_output', fileFilter='Microsoft Excel (*.xlsx);;Open Document Spreadsheet (*.ods)', createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(3, model_feedback)
        results = {}
        outputs = {}

        # Raster pixels to points
        alg_params = {
            'FIELD_NAME': 'VALUE',
            'INPUT_RASTER': parameters['InputRaster'],
            'RASTER_BAND': 1,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['RasterPixelsToPoints'] = processing.run('native:pixelstopoints', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Add X/Y fields to layer
        alg_params = {
            'CRS': QgsCoordinateReferenceSystem('EPSG:32645'),
            'INPUT': outputs['RasterPixelsToPoints']['OUTPUT'],
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['AddXyFieldsToLayer'] = processing.run('native:addxyfields', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Export to spreadsheet
        alg_params = {
            'FORMATTED_VALUES': False,
            'LAYERS': outputs['AddXyFieldsToLayer']['OUTPUT'],
            'OVERWRITE': True,
            'USE_ALIAS': True,
            'OUTPUT': parameters['Spreadsheet_output']
        }
        outputs['ExportToSpreadsheet'] = processing.run('native:exporttospreadsheet', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Spreadsheet_output'] = outputs['ExportToSpreadsheet']['OUTPUT']
        return results

    def name(self):
        return 'Raster to Points with X/Y Coordinates'

    def displayName(self):
        return 'Raster to Points with X/Y Coordinates'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return RasterToPointsWithXyCoordinates()

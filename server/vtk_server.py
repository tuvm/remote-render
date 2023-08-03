r"""
    This module is a VTK Web server application.
    The following command line illustrates how to use it::

        $ vtkpython .../vtk_server.py

    Any VTK Web executable script comes with a set of standard arguments that
    can be overriden if need be::
        --host localhost
             Interface on which the HTTP server will listen.

        --port 8080
             Port number on which the HTTP server will listen.

        --content /path-to-web-content/
             Directory that you want to serve as static web content.
             By default, this variable is empty which means that we rely on another server
             to deliver the static content and the current process only focuses on the
             WebSocket connectivity of clients.

        --authKey wslink-secret
             Secret key that should be provided by the client to allow it to make any
             WebSocket communication. The client will assume if none is given that the
             server expects "wslink-secret" as the secret key.
"""

# import to process args
import sys
import os

# import vtk modules.
import vtk
from vtk.web import protocols
from vtk.web import wslink as vtk_wslink
from wslink import server

#!/usr/bin/env python

# noinspection PyUnresolvedReferences
#!/usr/bin/env python
# -*- coding: utf-8 -*-

# noinspection PyUnresolvedReferences
import vtk.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtk.vtkRenderingOpenGL2
from vtk.vtkCommonColor import vtkNamedColors
# from vtk.vtkCommonDataModel import vtkPieceWiseFunction
from vtk.vtkIOXML import vtkXMLImageDataReader
from vtk import (
    vtkActor,
    vtkDataSetMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer,
    vtkColorTransferFunction,
    vtkPiecewiseFunction,
    vtkVolume,
    vtkSmartVolumeMapper,
    vtkVolumeProperty
)

try:
    import argparse
except ImportError:
    # since  Python 2.6 and earlier don't have argparse, we simply provide
    # the source for the same as _argparse and we use it instead.
    from vtk.util import _argparse as argparse

# =============================================================================
# Create custom ServerProtocol class to handle clients requests
# =============================================================================

def get_program_parameters():
    import argparse
    description = 'The skin and bone is extracted from a CT dataset of the head.'
    epilogue = '''
    Derived from VTK/Examples/Cxx/Medical2.cxx
    This example reads a volume dataset, extracts two isosurfaces that
    represent the skin and bone, and then displays it.
    '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                    formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('filename', help='FullHead.mhd.')
    args = parser.parse_args()
    return args.filename


def vtk_version_ok(major, minor, build):
    """
    Check the VTK version.

    :param major: Major version.
    :param minor: Minor version.
    :param build: Build version.
    :return: True if the requested VTK version is greater or equal to the actual VTK version.
    """
    needed_version = 10000000000 * int(major) + 100000000 * int(minor) + int(build)
    try:
        vtk_version_number = VTK_VERSION_NUMBER
    except AttributeError:  # as error:
        ver = vtkVersion()
        vtk_version_number = 10000000000 * ver.GetVTKMajorVersion() + 100000000 * ver.GetVTKMinorVersion() \
                            + ver.GetVTKBuildVersion()
    if vtk_version_number >= needed_version:
        return True
    else:
        return False
    
def applyPointsToRGBFunction(points, cfun):
    cfun.RemoveAllPoints()
    for point in points:
        [x, r, g, b] = point
        cfun.AddRGBPoint(x, r, g, b)
    # points.forEach(([x, r, g, b]) => cfun.addRGBPoint(x, r, g, b));

def applyPointsToPiecewiseFunction(points, pwf):
    pwf.RemoveAllPoints()
    for point in points:
        [x, y] = point
        pwf.AddPoint(x, y)
    # points.forEach(([x, y]) => pwf.addPoint(x, y));

class _WebCone(vtk_wslink.ServerProtocol):

    # Application configuration
    view    = None
    authKey = "wslink-secret"

    def initialize(self):
        global renderer, renderWindow, renderWindowInteractor, cone, mapper, actor

        # Bring used components
        self.registerVtkWebProtocol(protocols.vtkWebMouseHandler())
        self.registerVtkWebProtocol(protocols.vtkWebViewPort())
        self.registerVtkWebProtocol(protocols.vtkWebViewPortImageDelivery())
        self.registerVtkWebProtocol(protocols.vtkWebViewPortGeometryDelivery())

        # Update authentication key to use
        self.updateSecret(_WebCone.authKey)

        # Create default pipeline (Only once for all the session)
        if not _WebCone.view:
            # VTK specific code
            # renderer = vtk.vtkRenderer()
            # renderWindow = vtk.vtkRenderWindow()
            # renderWindow.AddRenderer(renderer)

            # renderWindowInteractor = vtk.vtkRenderWindowInteractor()
            # renderWindowInteractor.SetRenderWindow(renderWindow)
            # renderWindowInteractor.GetInteractorStyle().SetCurrentStyleToTrackballCamera()

            # cone = vtk.vtkConeSource()
            # mapper = vtk.vtkPolyDataMapper()
            # actor = vtk.vtkActor()

            # mapper.SetInputConnection(cone.GetOutputPort())
            # actor.SetMapper(mapper)

            # renderer.AddActor(actor)
            # renderer.ResetCamera()
            # renderWindow.Render()

            colors = vtkNamedColors()

            file_name = 'output.vti' #get_program_parameters()

            # Read the source file.
            reader = vtkXMLImageDataReader()
            reader.SetFileName(file_name)

            # Create the mapper that creates graphics elements
            mapper = vtkSmartVolumeMapper()
            mapper.SetInputConnection(reader.GetOutputPort())

            # Create the Actor
            # actor = vtkActor()
            # actor.SetMapper(mapper)
            # show the edges of the image grid
            # volProperty.SetRepresentationToWireframe()
            # volProperty.SetRGBTransferFunction()

            preset = {
                'name': 'CT-Coronary-Arteries-2',
                'gradientOpacity': '4 0 1 255 1',
                'specularPower': '1',
                'scalarOpacity':
                '14 -2048 0 142.677 0 145.016 0.116071 192.174 0.5625 217.24 0.776786 384.347 0.830357 3661 0.830357',
                'id': 'vtkMRMLVolumePropertyNode11',
                'specular': '0',
                'shade': '1',
                'ambient': '0.2',
                'colorTransfer':
                '28 -2048 0 0 0 142.677 0 0 0 145.016 0.615686 0 0.0156863 192.174 0.909804 0.454902 0 217.24 0.972549 0.807843 0.611765 384.347 0.909804 0.909804 1 3661 1 1 1',
                'selectable': 'true',
                'diffuse': '1',
                'interpolation': '1',
                'effectiveRange': '142.677 384.347',
            }

            splitColor = preset['colorTransfer'].split(' ')
            colorTransferArray = [float(it) for it in splitColor[1:]]

            cfun = vtkColorTransferFunction()
            print(colorTransferArray)

            normColorTransferValuePoints = list()
            for i in range(0, len(colorTransferArray), 4): #(let i = 0; i < colorTransferArray.length; i += 4) {
                value = colorTransferArray[i]
                r = colorTransferArray[i + 1]
                g = colorTransferArray[i + 2]
                b = colorTransferArray[i + 3]

                normColorTransferValuePoints.append([value, r, g, b])

            print(normColorTransferValuePoints)

            applyPointsToRGBFunction(normColorTransferValuePoints, cfun)

            print(cfun)

            splitOpacity = preset['scalarOpacity'].split(' ')
            scalarOpacityArray = [float(it) for it in splitOpacity[1:]]

            ofun = vtkPiecewiseFunction()

            normPoints = list()
            # for (let i = 0; i < scalarOpacityArray.length; i += 2) {
            for j in range(0, len(scalarOpacityArray), 2):
                print(j)
                value = scalarOpacityArray[j]
                opacity = scalarOpacityArray[j + 1]

            # // value = (value - min) / width;
                normPoints.append([value, opacity])

            print(normPoints)

            applyPointsToPiecewiseFunction(normPoints, ofun)
            
            # mapper.SetLookupTable(cfun)

            volProperty =  vtkVolumeProperty()

            volProperty.SetColor(cfun)
            volProperty.SetScalarOpacity(ofun)

            # volProperty.SetScalarOpacity(ofun)
            # volProperty.SetUseGradientOpacity(0, True)
            # volProperty.SetGradientOpacityMinimumValue(0, 0)
            # volProperty.SetGradientOpacityMinimumOpacity(0, 1)

            # volProperty.SetGradientOpacityMaximumValue(0, 255)
            # volProperty.SetGradientOpacityMaximumOpacity(0, 1)
            # volProperty.SetInterpolationTypeToLinear()
            volProperty.SetAmbient(float(preset['ambient']))
            volProperty.SetShade(int(preset['shade']))
            volProperty.SetDiffuse(float(preset['diffuse']))
            volProperty.SetSpecular(float(preset['specular']))
            volProperty.SetSpecularPower(float(preset['specularPower']))
            # volProperty.SetRange([-1000, 1000])
            volProperty.SetScalarOpacityUnitDistance(0, 1.5)
            print(volProperty)

            vol = vtkVolume()
            vol.SetMapper(mapper)
            vol.SetProperty(volProperty)

            # Create the Renderer
            renderer = vtkRenderer()
            renderer.AddActor(vol)
            renderer.ResetCamera()
            # renderer.SetBackground(colors.GetColor3d('Silver'))

            # Create the RendererWindow
            renderer_window = vtkRenderWindow()
            renderer_window.AddRenderer(renderer)
            # renderer_window.SetSize(640, 480)
            # renderer_window.SetWindowName('ReadImageData')

            # Create the RendererWindowInteractor and display the vti file
            interactor = vtkRenderWindowInteractor()
            interactor.SetRenderWindow(renderer_window)
            interactor.GetInteractorStyle().SetCurrentStyleToTrackballCamera()
            # interactor.EnableRenderOff()
            # interactor.Initialize()
            # interactor.Start()

            # VTK Web application specific
            # _WebCone.view = renderer_window
            self.getApplication().GetObjectIdMap().SetActiveObject("VIEW", renderer_window)

# =============================================================================
# Main: Parse args and start server
# =============================================================================

if __name__ == "__main__":
    # Create argument parser
    parser = argparse.ArgumentParser(description="VTK/Web Cone web-application")

    # Add default arguments
    server.add_arguments(parser)

    # Extract arguments
    args = parser.parse_args()

    # Configure our current application
    _WebCone.authKey = args.authKey

    # Start server
    server.start_webserver(options=args, protocol=_WebCone)
# WorkflowNo_643
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_643
doc: A workflow including the tool(s) XTandemPipeline, PChopper, OpenSWATH, OpenMS, OpenSWATH.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_3622" # Gemini SQLite format
  input_2:
    type: File
    format: "http://edamontology.org/format_3713" # Mascot .dat file
  input_3:
    type: File
    format: "http://edamontology.org/format_3246" # TraML
steps:
  XTandemPipeline_01:
    run: add-path-to-the-implementation/XTandemPipeline.cwl 
    in:
      XTandemPipeline_in_1: input_2
    out: [XTandemPipeline_out_1, XTandemPipeline_out_2]
  PChopper_02:
    run: add-path-to-the-implementation/PChopper.cwl 
    in:
      PChopper_in_1: XTandemPipeline_01/XTandemPipeline_out_2
    out: [PChopper_out_1]
  OpenSWATH_03:
    run: add-path-to-the-implementation/OpenSWATH.cwl 
    in:
      OpenSWATH_in_1: input_1
      OpenSWATH_in_2: input_3
    out: [OpenSWATH_out_1]
  OpenMS_04:
    run: add-path-to-the-implementation/OpenMS.cwl 
    in:
      OpenMS_in_1: OpenSWATH_03/OpenSWATH_out_1
      OpenMS_in_2: PChopper_02/PChopper_out_1
      OpenMS_in_3: XTandemPipeline_01/XTandemPipeline_out_1
    out: [OpenMS_out_1, OpenMS_out_2]
  OpenSWATH_05:
    run: add-path-to-the-implementation/OpenSWATH.cwl 
    in:
      OpenSWATH_in_1: OpenMS_04/OpenMS_out_2
    out: [OpenSWATH_out_1]
outputs:
  output_1:
    type: File
    format: "http://edamontology.org/format_3622" # Gemini SQLite format
    outputSource: OpenSWATH_05/OpenSWATH_out_1

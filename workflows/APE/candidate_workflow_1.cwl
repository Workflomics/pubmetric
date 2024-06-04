# WorkflowNo_0
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_0
doc: A workflow including the tool(s) XTandemPipeline, OpenMS, dig, DeconMSn, PeptideShaker.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_3654" # mzXML
  input_2:
    type: File
    format: "http://edamontology.org/format_3845" # HSAML
  input_3:
    type: File
    format: "http://edamontology.org/format_3711" # X!Tandem XML
steps:
  XTandemPipeline_01:
    run: add-path-to-the-implementation/XTandemPipeline.cwl 
    in:
      XTandemPipeline_in_1: input_3
    out: [XTandemPipeline_out_1, XTandemPipeline_out_2]
  OpenMS_02:
    run: add-path-to-the-implementation/OpenMS.cwl 
    in:
      OpenMS_in_1: input_1
      OpenMS_in_2: input_2
      OpenMS_in_3: input_3
    out: [OpenMS_out_1, OpenMS_out_2]
  dig_03:
    run: add-path-to-the-implementation/dig.cwl 
    in:
      dig_in_1: OpenMS_02/OpenMS_out_1
    out: [dig_out_1]
  DeconMSn_04:
    run: add-path-to-the-implementation/DeconMSn.cwl 
    in:
      DeconMSn_in_1: input_1
      DeconMSn_in_2: input_1
    out: [DeconMSn_out_1, DeconMSn_out_2, DeconMSn_out_3]
  PeptideShaker_05:
    run: add-path-to-the-implementation/PeptideShaker.cwl 
    in:
      PeptideShaker_in_1: dig_03/dig_out_1
      PeptideShaker_in_2: XTandemPipeline_01/XTandemPipeline_out_1
      PeptideShaker_in_3: DeconMSn_04/DeconMSn_out_3
    out: [PeptideShaker_out_1, PeptideShaker_out_2, PeptideShaker_out_3, PeptideShaker_out_4]
outputs:
  output_1:
    type: File
    format: "http://edamontology.org/format_3592" # BMP
    outputSource: PeptideShaker_05/PeptideShaker_out_1

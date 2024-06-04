# WorkflowNo_702
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_702
doc: A workflow including the tool(s) MS-Isotope, ProFound, OpenMS, MassChroQ, OpenSWATH.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_1996" # pair
  input_2:
    type: File
    format: "http://edamontology.org/format_1957" # raw
  input_3:
    type: File
    format: "http://edamontology.org/format_2549" # OBO
steps:
  MS-Isotope_01:
    run: add-path-to-the-implementation/MS-Isotope.cwl 
    in:
      MS-Isotope_in_1: input_2
    out: [MS-Isotope_out_1]
  ProFound_02:
    run: add-path-to-the-implementation/ProFound.cwl 
    in:
      ProFound_in_1: input_3
    out: [ProFound_out_1]
  OpenMS_03:
    run: add-path-to-the-implementation/OpenMS.cwl 
    in:
      OpenMS_in_1: input_3
      OpenMS_in_2: MS-Isotope_01/MS-Isotope_out_1
      OpenMS_in_3: ProFound_02/ProFound_out_1
    out: [OpenMS_out_1, OpenMS_out_2]
  MassChroQ_04:
    run: add-path-to-the-implementation/MassChroQ.cwl 
    in:
      MassChroQ_in_1: OpenMS_03/OpenMS_out_1
    out: [MassChroQ_out_1]
  OpenSWATH_05:
    run: add-path-to-the-implementation/OpenSWATH.cwl 
    in:
      OpenSWATH_in_1: MassChroQ_04/MassChroQ_out_1
    out: [OpenSWATH_out_1]
outputs:
  output_1:
    type: File
    format: "http://edamontology.org/format_3654" # mzXML
    outputSource: OpenSWATH_05/OpenSWATH_out_1

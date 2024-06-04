# WorkflowNo_411
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_411
doc: A workflow including the tool(s) OpenSWATH, mres2x, EncyclopeDIA, OpenMS, OpenSWATH.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_1929" # FASTA
  input_2:
    type: File
    format: "http://edamontology.org/format_3654" # mzXML
  input_3:
    type: File
    format: "http://edamontology.org/format_3713" # Mascot .dat file
steps:
  OpenSWATH_01:
    run: add-path-to-the-implementation/OpenSWATH.cwl 
    in:
      OpenSWATH_in_1: input_3
    out: [OpenSWATH_out_1]
  mres2x_02:
    run: add-path-to-the-implementation/mres2x.cwl 
    in:
      mres2x_in_1: input_3
    out: [mres2x_out_1]
  EncyclopeDIA_03:
    run: add-path-to-the-implementation/EncyclopeDIA.cwl 
    in:
      EncyclopeDIA_in_1: OpenSWATH_01/OpenSWATH_out_1
      EncyclopeDIA_in_2: input_1
    out: [EncyclopeDIA_out_1]
  OpenMS_04:
    run: add-path-to-the-implementation/OpenMS.cwl 
    in:
      OpenMS_in_1: mres2x_02/mres2x_out_1
      OpenMS_in_2: input_2
      OpenMS_in_3: EncyclopeDIA_03/EncyclopeDIA_out_1
    out: [OpenMS_out_1, OpenMS_out_2]
  OpenSWATH_05:
    run: add-path-to-the-implementation/OpenSWATH.cwl 
    in:
      OpenSWATH_in_1: OpenMS_04/OpenMS_out_2
    out: [OpenSWATH_out_1]
outputs:
  output_1:
    type: File
    format: "http://edamontology.org/format_3654" # mzXML
    outputSource: OpenSWATH_05/OpenSWATH_out_1

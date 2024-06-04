# WorkflowNo_257
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_257
doc: A workflow including the tool(s) CPM, Jtraml, MSiReader, OpenSWATH, Mascot Server.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_3162" # MAGE-TAB
  input_2:
    type: File
    format: "http://edamontology.org/format_3244" # mzML
  input_3:
    type: File
    format: "http://edamontology.org/format_1423" # Phylip distance matrix
steps:
  CPM_01:
    run: add-path-to-the-implementation/CPM.cwl 
    in:
      CPM_in_1: input_1
      CPM_in_2: input_3
    out: [CPM_out_1, CPM_out_2]
  Jtraml_02:
    run: add-path-to-the-implementation/Jtraml.cwl 
    in:
      Jtraml_in_1: input_3
    out: [Jtraml_out_1]
  MSiReader_03:
    run: add-path-to-the-implementation/MSiReader.cwl 
    in:
      MSiReader_in_1: CPM_01/CPM_out_1
      MSiReader_in_2: Jtraml_02/Jtraml_out_1
    out: [MSiReader_out_1, MSiReader_out_2]
  OpenSWATH_04:
    run: add-path-to-the-implementation/OpenSWATH.cwl 
    in:
      OpenSWATH_in_1: input_2
      OpenSWATH_in_2: input_1
    out: [OpenSWATH_out_1]
  Mascot Server_05:
    run: add-path-to-the-implementation/Mascot Server.cwl 
    in:
      Mascot Server_in_1: OpenSWATH_04/OpenSWATH_out_1
      Mascot Server_in_2: MSiReader_03/MSiReader_out_2
    out: [Mascot Server_out_1]
outputs:
  output_1:
    type: File
    format: "http://edamontology.org/format_3651" # MGF
    outputSource: Mascot Server_05/Mascot Server_out_1

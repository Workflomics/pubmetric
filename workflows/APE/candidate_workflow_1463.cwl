# WorkflowNo_1462
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_1462
doc: A workflow including the tool(s) dig, PeptideProphet, OpenMS, RelEx, qcmetrics.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_1929" # FASTA
  input_2:
    type: File
    format: "http://edamontology.org/format_2311" # EMBL-HTML
  input_3:
    type: File
    format: "http://edamontology.org/format_3311" # RNAML
steps:
  dig_01:
    run: add-path-to-the-implementation/dig.cwl 
    in:
      dig_in_1: input_1
    out: [dig_out_1]
  PeptideProphet_02:
    run: add-path-to-the-implementation/PeptideProphet.cwl 
    in:
      PeptideProphet_in_1: input_2
    out: [PeptideProphet_out_1]
  OpenMS_03:
    run: add-path-to-the-implementation/OpenMS.cwl 
    in:
      OpenMS_in_1: input_3
      OpenMS_in_2: dig_01/dig_out_1
      OpenMS_in_3: PeptideProphet_02/PeptideProphet_out_1
    out: [OpenMS_out_1, OpenMS_out_2]
  RelEx_04:
    run: add-path-to-the-implementation/RelEx.cwl 
    in:
      RelEx_in_1: OpenMS_03/OpenMS_out_1
    out: [RelEx_out_1]
  qcmetrics_05:
    run: add-path-to-the-implementation/qcmetrics.cwl 
    in:
      qcmetrics_in_1: RelEx_04/RelEx_out_1
    out: [qcmetrics_out_1]
outputs:
  output_1:
    type: File
    format: "http://edamontology.org/format_2532" # GenBank-HTML
    outputSource: qcmetrics_05/qcmetrics_out_1

# WorkflowNo_345
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_345
doc: A workflow including the tool(s) msConvert, mzRecal, Comet, idconvert, PeptideProphet, ProteinProphet.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_3247" # mzIdentML
  input_2:
    type: File
    format: "http://edamontology.org/format_1929" # FASTA
  input_3:
    type: File
    format: "http://edamontology.org/format_3712" # Thermo RAW
steps:
  msConvert_01:
    run: https://raw.githubusercontent.com/Workflomics/containers/main/cwl/tools/msConvert/msConvert.cwl
    in:
      msConvert_in_1: input_3
    out: [msConvert_out_1]
  mzRecal_02:
    run: https://raw.githubusercontent.com/Workflomics/containers/main/cwl/tools/mzRecal/mzRecal.cwl
    in:
      mzRecal_in_1: msConvert_01/msConvert_out_1
      mzRecal_in_2: input_1
    out: [mzRecal_out_1]
  Comet_03:
    run: https://raw.githubusercontent.com/Workflomics/containers/main/cwl/tools/Comet/Comet.cwl
    in:
      Comet_in_1: mzRecal_02/mzRecal_out_1
      Comet_in_2: input_2
    out: [Comet_out_1, Comet_out_2]
  idconvert_04:
    run: https://raw.githubusercontent.com/Workflomics/containers/main/cwl/tools/idconvert/idconvert_to_pepXML.cwl
    in:
      idconvert_in_1: Comet_03/Comet_out_2
    out: [idconvert_out_1]
  PeptideProphet_05:
    run: https://raw.githubusercontent.com/Workflomics/containers/main/cwl/tools/PeptideProphet/PeptideProphet.cwl
    in:
      PeptideProphet_in_1: idconvert_04/idconvert_out_1
      PeptideProphet_in_2: msConvert_01/msConvert_out_1
      PeptideProphet_in_3: input_2
    out: [PeptideProphet_out_1, PeptideProphet_out_2]
  ProteinProphet_06:
    run: https://raw.githubusercontent.com/Workflomics/containers/main/cwl/tools/ProteinProphet/ProteinProphet.cwl
    in:
      ProteinProphet_in_1: PeptideProphet_05/PeptideProphet_out_1
      ProteinProphet_in_2: input_2
    out: [ProteinProphet_out_1, ProteinProphet_out_2]
outputs:
  output_1:
    type: File
    format: "http://edamontology.org/format_3747" # protXML
    outputSource: ProteinProphet_06/ProteinProphet_out_1

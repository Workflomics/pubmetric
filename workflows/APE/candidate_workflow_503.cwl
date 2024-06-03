# WorkflowNo_502
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_502
doc: A workflow including the tool(s) msConvert, Comet, PeptideProphet, ProteinProphet, protXml2IdList, gProfiler.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_3654" # mzXML
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
  Comet_02:
    run: https://raw.githubusercontent.com/Workflomics/containers/main/cwl/tools/Comet/Comet.cwl
    in:
      Comet_in_1: input_1
      Comet_in_2: input_2
    out: [Comet_out_1, Comet_out_2]
  PeptideProphet_03:
    run: https://raw.githubusercontent.com/Workflomics/containers/main/cwl/tools/PeptideProphet/PeptideProphet.cwl
    in:
      PeptideProphet_in_1: Comet_02/Comet_out_1
      PeptideProphet_in_2: msConvert_01/msConvert_out_1
      PeptideProphet_in_3: input_2
    out: [PeptideProphet_out_1, PeptideProphet_out_2]
  ProteinProphet_04:
    run: https://raw.githubusercontent.com/Workflomics/containers/main/cwl/tools/ProteinProphet/ProteinProphet.cwl
    in:
      ProteinProphet_in_1: PeptideProphet_03/PeptideProphet_out_1
      ProteinProphet_in_2: input_2
    out: [ProteinProphet_out_1, ProteinProphet_out_2]
  protXml2IdList_05:
    run: https://raw.githubusercontent.com/Workflomics/containers/main/cwl/tools/protXml2IdList/protXml2IdList.cwl
    in:
      protXml2IdList_in_1: ProteinProphet_04/ProteinProphet_out_1
    out: [protXml2IdList_out_1]
  gProfiler_06:
    run: https://raw.githubusercontent.com/Workflomics/containers/main/cwl/tools/gProfiler/gProfiler.cwl
    in:
      gProfiler_in_1: protXml2IdList_05/protXml2IdList_out_1
    out: [gProfiler_out_1]
outputs:
  output_1:
    type: File
    format: "http://edamontology.org/format_3781" # PubAnnotation format
    outputSource: gProfiler_06/gProfiler_out_1

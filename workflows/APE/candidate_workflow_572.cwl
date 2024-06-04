# WorkflowNo_571
# This workflow is generated by APE (https://github.com/sanctuuary/APE).
cwlVersion: v1.2
class: Workflow

label: WorkflowNo_571
doc: A workflow including the tool(s) ICPL_ESIQuant, MS-Isotope, MS-Fit, OpenMS, OpenSWATH.

inputs:
  input_1:
    type: File
    format: "http://edamontology.org/format_3652" # dta
  input_2:
    type: File
    format: "http://edamontology.org/format_3713" # Mascot .dat file
  input_3:
    type: File
    format: "http://edamontology.org/format_1641" # affymetrix-exp
steps:
  ICPL_ESIQuant_01:
    run: add-path-to-the-implementation/ICPL_ESIQuant.cwl 
    in:
      ICPL_ESIQuant_in_1: input_2
    out: [ICPL_ESIQuant_out_1]
  MS-Isotope_02:
    run: add-path-to-the-implementation/MS-Isotope.cwl 
    in:
      MS-Isotope_in_1: ICPL_ESIQuant_01/ICPL_ESIQuant_out_1
    out: [MS-Isotope_out_1]
  MS-Fit_03:
    run: add-path-to-the-implementation/MS-Fit.cwl 
    in:
      MS-Fit_in_1: input_3
    out: [MS-Fit_out_1]
  OpenMS_04:
    run: add-path-to-the-implementation/OpenMS.cwl 
    in:
      OpenMS_in_1: input_1
      OpenMS_in_2: MS-Isotope_02/MS-Isotope_out_1
      OpenMS_in_3: MS-Fit_03/MS-Fit_out_1
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

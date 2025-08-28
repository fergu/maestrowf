# MEP 003 - Human Readable Hashing: Compact and sortable step name hashing

## Abstract

Step naming and workspace naming behaviors in Maestro is a frequent pain point in many studies.  The default naming convention aimed to provide quick lookup by encoding parameter names and values in the step name and workspace names.  Some parameter types, such as floating point numbers, result in readability problems with only a few parameters attached to a step, while 10's of parameters can blow out system path length limits, preventing study execution altogether.  There is a relief valve for this in the form of workspace hashing, however this trades readability for ~compactness owing to the use of hashing algorithms such as md5.  This proposal aims to relieve both tensions, maintaining compactness, human readability, and still guaranteeing uniqueness of the hash.

## Parameter Combinations

A core identifier of a Maestro step instance is the parameter combination.  We shall refer to a simple study below to illustrate how parameter combinations work and the different kinds that can be attached to a study step instance.

### Demo Study Spec
``` yaml
description:
  name: parameter_combo_demo
  description: |
      Simple study used to demonstrate parameter combinations and a new
	  workspace/step hashing implementation
	  
study:
  - name: step-1
    description: Simple step using a subset of parameters
	run:
	  cmd: |
	    echo "Used Parameters: PARAM_1: $(PARAM_1)"
		
  - name: step-2
    description: Simple step using all parameters
	run:
	  cmd: |
	    echo "Used Parameters: PARAM_1: $(PARAM_1), PARAM_2: $(PARAM_2)"
		
global.parameters:
  PARAM_1:
    values: [1, 1, 2, 2]
	labels: PARAM_1.%%
	
  PARAM_2:
    values: [3, 5, 3, 5]
```

### Demo Study Parameter Combinations
This results in the following set of parameter combinations:

| **Parameter** | **Combo 1** | **Combo 2** | **Combo 3** | **Combo 4** |
| :-----------: | :---------: | :---------: | :---------: | :---------: |
| PARAM_1       |           1 |           1 |           2 |           2 |
| PARAM_2       |           3 |           5 |           3 |           5 |

Now we take into account the concept of 'used parameters', which is what Maestro uses under the covers to build the graph of instantiated steps.  Each column in this table represents one parameter combination, for a toatal of four.  As there are four unique values of these tuples, any step using both parameters (the steps' used parameters) will have four instances.  We see `step-2` uses both, so we have four instances of this step in the study. However, `step-1` only uses one of the parameters, `PARAM_1`, and we can see there are only 2 unique values, leading to only two instances of `step-1`, as shown in the topology below:

### Demo Study Topology
``` mermaid
flowchart TD;
    A(study-root) --> step_1_1;
	subgraph step_1_1 [step-1]
	  subgraph S1COMBO1 [Step-1 Used Combo 1]
	    B(PARAM_1 = 1);
      end
	end
	A --> step_1_2;
	subgraph step_1_2 [step-1]
	  subgraph S1COMBO2 [Step-1 Used Combo 2]
	    C(PARAM_1 = 2);
      end
	end
	step_1_1 --> step_2_1;
	subgraph step_2_1 [step-2]
	  subgraph S2COMBO1 [Step-2 Used Combo 1]
	    D(PARAM_1 = 1\nPARAM_2 = 3);
      end
	end
	step_1_1 --> step_2_2;
	subgraph step_2_2 [step-2]
	  subgraph S2COMBO2 [Step-2 Used Combo 2]
	    E(PARAM_1 = 1\nPARAM_2 = 5);
      end
	end	
	step_1_2 --> step_2_3;
	subgraph step_2_3 [step-2]
	  subgraph S2COMBO3 [Step-2 Used Combo 3]
	    F(PARAM_1 = 2\nPARAM_2 = 3);
      end
	end
	step_1_2 --> step_2_4;
	subgraph step_2_4 [step-2]
	  subgraph S2COMBO4 [Step-2 Used Combo 4]
	    G(PARAM_1 = 2\nPARAM_2 = 5);
      end
	end
```

### Demo Step Names

#### Default Naming ~v1.1

Default names for steps, and workspaces, uses the parameter labels as of v1.1.11, current release as of this draft.  These labels are meant to be more human friendly formats of parameter name.values that identify a specific parameter value.  Step/workspace naming uses the used parameter combinations' labels, as shown below:

| **Used Combo \#**   | **Step Name/Workspace Name** |
| :-----------:       | :---------:                  |
| step-1 used combo 1 | step-1_PARAM_1.1             |
| step-1 used combo 2 | step-1_PARAM_1.2             |
| step-2 used combo 1 | step-2_PARAM_1.1.PARAM_2.3   |
| step-2 used combo 2 | step-2_PARAM_1.1.PARAM_2.5   |
| step-2 used combo 3 | step-2_PARAM_1.2.PARAM_2.3   |
| step-2 used combo 4 | step-2_PARAM_1.2.PARAM_2.5   |

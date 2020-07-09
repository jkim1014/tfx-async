
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os

from typing import Any, Dict, List, Text, cast

from tfx import types
from tfx.components.base import base_executor
from tfx.components.base import executor_spec
from tfx.orchestration.config import base_component_config
from tfx.orchestration.launcher import base_component_launcher_2 


class LoopedComponentLauncher(base_component_launcher_2.BaseComponentLauncher2):
  """Responsible for launching a python executor.

  The executor will be launched in the same process of the rest of the
  component, i.e. its driver and publisher.
  """

  @classmethod
  def can_launch(
      cls, component_executor_spec: executor_spec.ExecutorSpec,
      component_config: base_component_config.BaseComponentConfig) -> bool:
    """Checks if the launcher can launch the executor spec."""
    if component_config:
      return False

    return isinstance(component_executor_spec, executor_spec.ExecutorClassSpec)

  def _run_executor(self, execution_id: int,
                    input_dict: Dict[Text, List[types.Artifact]],
                    output_dict: Dict[Text, List[types.Artifact]],
                    exec_properties: Dict[Text, Any]) -> None:
    """Execute underlying component implementation."""
    executor_context = base_executor.BaseExecutor.Context(
        beam_pipeline_args=self._beam_pipeline_args,
        tmp_dir=os.path.join(self._pipeline_info.pipeline_root, '.temp', ''),
        unique_id=str(execution_id))

    executor_class_spec = cast(executor_spec.ExecutorClassSpec,
                               self._component_executor_spec)

    # Type hint of component will cause not-instantiable error as
    # component.executor is Type[BaseExecutor] which has an abstract function.
    executor = executor_class_spec.executor_class(
        executor_context)  # type: ignore

    executor.Do(input_dict, output_dict, exec_properties)

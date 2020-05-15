# -*- coding: utf-8 -*-
# Copyright 2020 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Task to run Photorec on disk images and retrieve deleted files ."""
from __future__ import unicode_literals

import logging
import json
import os

from turbinia import TurbiniaException
from turbinia.workers import TurbiniaTask
from turbinia.evidence import PhotorecOutput


class PhotorecTask(TurbiniaTask):

  def run(self, evidence, result):
    """Task to execute photorec.

    Args:
        evidence (Evidence object):  The evidence we will process.
        result (TurbiniaTaskResult): The object to place task results into.
    Returns:
        TurbiniaTaskResult object.
    """
    # Create the new Evidence object that will be generated by this Task.
    output_evidence = PhotorecOutput()
    # Create a path that we can write the new file to.
    base_name = os.path.basename(evidence.local_path)
    output_file_path = os.path.join(self.output_dir, 'photorec_output')
    photorec_log = os.path.join(self.output_dir, 'photorec.log')
    # Add the output path to the evidence so we can automatically save it
    # later.
    output_evidence.local_path = output_file_path
    try:
      # Generate the command we want to run.
      cmd = 'photorec /log /d {0:s} /cmd {1:s}  options,paranoid,keep_corrupted_fille,search'.format(
          output_file_path, evidence.local_path)
      # Add a log line to the result that will be returned.
      result.log('Running photorec as [{0:s}]'.format(cmd))
      # Actually execute the binary
      self.execute(
          cmd, result, log_files=[photorec_log], new_evidence=[output_evidence],
          shell=True)
      output_evidence.compress()
      result.close(
          self, success=True, status='Photorec task completed successfully.')
    except TurbiniaException as exception:
      result.close(self, success=False, status=str(exception))

    return result
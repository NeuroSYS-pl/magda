from typing import List
from magda.module.module import Module
from magda.decorators.registering import register
from magda.decorators.finalizing import finalize


@register('ModuleDecoratedMock')
@finalize
class ModuleDecoratedMock(Module.Runtime):
    def run(self, data: List[Module.Result], **kwargs):
        return 'ModuleDecoratedMock'

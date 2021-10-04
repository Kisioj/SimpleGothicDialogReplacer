import antlr4

import re
import sys

from grammar.DaedalusLexer import DaedalusLexer
from grammar.DaedalusParser import DaedalusParser
from grammar.DaedalusVisitor import DaedalusVisitor
from syntax_error_listener import SyntaxErrorListener


class DaedalusSniffer:
    def __init__(self):
        self.texts = []

    def sniff(self, file_path):
        with open(file_path, encoding='windows-1250') as file:
            content = file.read()
            lines = content.split('\n')

        input_stream = antlr4.InputStream(content)
        lexer = DaedalusLexer(input_stream)
        token_stream = antlr4.CommonTokenStream(lexer)
        parser = DaedalusParser(token_stream)

        listener = SyntaxErrorListener()
        parser.addErrorListener(listener)
        parse_tree = parser.daedalusFile()

        if listener.errors_count:
            msg = f"{listener.errors_count} syntax error generated"
            print(msg, file=sys.stderr)
            return

        sniffing_visitor = SniffingVisitor(file_path, lines)
        sniffing_visitor.visit(parse_tree)

        self.texts.extend(sniffing_visitor.texts)

        with open(file_path, 'w', encoding='windows-1250') as file:
            file.write('\n'.join(lines))


IGNORE_FUNCTIONS = {
    'PRINTDEBUGNPC',
    'PLAYVIDEO',
    'PLAYVIDEOEX',
    'INTRODUCECHAPTER',

    'NPC_EXCHANGEROUTINE',
    'NPC_ISONFP',
    'NPC_PLAYANI',
    'NPC_STOPANI',
    'NPC_GETDISTTOWP',

    'B_STARTOTHERROUTINE',
    'B_SETNPCVISUAL',
    'B_SAY',
    'B_SAY_OVERLAY',

    'DOC_SETPAGE',
    'DOC_SETLEVEL',

    'MDL_SETVISUAL',
    'MDL_SETVISUALBODY',
    'MDL_APPLYOVERLAYMDS',
    'MDL_REMOVEOVERLAYMDS',
    'MDL_APPLYOVERLAYMDSTIMED',
    'MDL_STARTFACEANI',
    'MDL_APPLYRANDOMANI',
    'MDL_APPLYRANDOMANIFREQ',

    'SND_PLAY',
    'SND_PLAY3D',

    'WLD_ASSIGNROOMTOGUILD',
    'WLD_INSERTNPC',
    'WLD_INSERTITEM',
    'WLD_SETMOBROUTINE',
    'WLD_PLAYEFFECT',
    'WLD_STOPEFFECT',
    'WLD_ISFPAVAILABLE',
    'WLD_ISNEXTFPAVAILABLE',
    'WLD_DETECTNPC',
    'WLD_ISMOBAVAILABLE',

    'AI_OUTPUT',
    'AI_PLAYANI',
    'AI_PLAYANIBS',
    'AI_GOTOFP',
    'AI_GOTONEXTFP',
    'AI_GOTOWP',
    'AI_STOPFX',
    'AI_USEMOB',
    'AI_TELEPORT',
    'AI_POINTAT',

    'HLP_STRCMP',

    'MOB_HASITEMS',

    # 'NOTE',
    # 'DOC_PRINTLINE',
    # 'DOC_PRINTLINES',
    # 'AI_PRINTSCREEN',
    # 'PRINTSCREEN',
    # 'PRINT',
    # 'START_MAIN_QUEST',
    # 'INFO_ADDCHOICE',
    # 'CLOSE_MISSION',
    # 'B_LOGENTRY',
    # 'FAILED_MISSION',
    # 'B_FINISHMISSIONBAGIENNESKARBY',
}

IGNORE_ATTRIBUTES = {
    'SPELLFXINSTANCENAMES',
    'SPELLFXANILETTERS',
    'SPELLANINAME',
    'VISUALFXNAME',

    'VISUAL',
    'VISUAL_CHANGE',
    'EFFECT',
    'SCEMENAME',

    # 'VISUALFXNAME',

    # 'NAME',
    # 'DESCRIPTION',
    # 'TEXT[0]',
    # 'TEXT[1]',
    # 'TEXT[2]',
    # 'TEXT[3]',
    # 'TEXT[4]',
    # 'TEXT[5]',
}

IGNORE_TRAILINGS = {
    '.TGA"',
    '.3DS"',
    '.ASC"',
    '.BIK"',
    '.MDS"',
}

IGNORE_INSTANCE_PARENTS = {
    'C_GILVALUES',
    'C_SVM',
    'JOLY_ITEM',
}


class SniffingVisitor(DaedalusVisitor):
    def __init__(self, file_path, lines, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.file_path = file_path
        self.short_path = file_path.split('/Scripts/Content')[-1]
        self.relative_file_path = file_path.split('/Scripts')[-1]
        self.lines = lines
        self.texts = []

    def visitValueExpression(self, ctx: DaedalusParser.ValueExpressionContext):
        text = ctx.getText()
        if text.startswith('"') and text.endswith('"') and re.search(r'[a-zA-Z\u0400-\u04FF]', text):
            if (text.upper()[-5:] in IGNORE_TRAILINGS) or text.startswith('"$') or '_' in text or '}}' in text:
                return

            print(f'{text}\t\t\t\t\t\t\t\t\t\t({self.short_path}:{ctx.stop.line}')
            stripped_text = text.strip('"')
            self.texts.append((stripped_text, f':{ctx.stop.line}'))
            self.lines[ctx.stop.line - 1] = self.lines[ctx.stop.line - 1].replace(text, f'"{{{{{stripped_text}}}}}"')

        return super().visitValueExpression(ctx)

    def visitFunctionCall(self, ctx: DaedalusParser.FunctionCallContext):
        upper_name = ctx.nameNode().getText().upper()
        if upper_name in IGNORE_FUNCTIONS or upper_name.startswith('TA_'):
            return
        return super().visitFunctionCall(ctx)

    def visitConstArrayDef(self, ctx: DaedalusParser.ConstArrayDefContext):
        if ctx.nameNode().getText().upper() in IGNORE_ATTRIBUTES:
            return
        return super().visitConstArrayDef(ctx)

    def visitConstValueDef(self, ctx: DaedalusParser.ConstValueDefContext):
        if ctx.nameNode().getText().upper() in IGNORE_ATTRIBUTES:
            return
        return super().visitConstValueDef(ctx)

    def visitAssignment(self, ctx: DaedalusParser.AssignmentContext):
        if ctx.reference().getText().upper() in IGNORE_ATTRIBUTES:
            return
        return super().visitAssignment(ctx)

    def visitInstanceDef(self, ctx: DaedalusParser.InstanceDefContext):
        if ctx.parentReference().getText().upper() in IGNORE_INSTANCE_PARENTS:
            return
        return super().visitInstanceDef(ctx)

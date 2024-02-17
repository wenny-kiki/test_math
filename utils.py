from Configration import *

class BasicTools:
    @staticmethod
    def plusTerms(in_vars):
        """
        >>> BasicTools.plusTerms(['x', 'y', 'z', 'a', 'b'])
        'x + y + z + a + b'
        """
        t = ''
        for v in in_vars:
            t = t + v + ' + '
        return t[0:-3]

    @staticmethod
    def minusTerms(in_vars):
        """
        >>> BasicTools.minusTerms(['x', 'y', 'z', 'a', 'b'])
        'x - y - z - a - b'
        """
        t = ''
        for v in in_vars:
            t = t + v + ' - '
        return t[0:-3]

    @staticmethod
    def getVariables_From_Constraints(C):
        V = set([])
        for s in C:
            temp = s.strip()
            temp = temp.replace(' + ', '   ')
            temp = temp.replace(' - ', '   ')
            temp = temp.replace(' * ', '   ')
            temp = temp.replace(' >= ', '   ')
            temp = temp.replace(' <= ', '   ')
            temp = temp.replace(' = ', '   ')
            temp = temp.replace(' -> ', '   ')
            temp = temp.replace(' AND ', '     ')
            temp = temp.replace(' OR ', '    ')
            temp = temp.replace(' MAX ', '     ')
            temp = temp.replace(' MIN ', '     ')
            temp = temp.replace(' , ', '   ')
            temp = temp.replace(' ( ', '   ')
            temp = temp.replace(' ) ', '   ')
            temp = temp.replace(' [ ', '   ')
            temp = temp.replace(' ] ', '   ')
            temp = temp.split()
            for v in temp:
                if not v.lstrip('-').isdecimal():
                    V.add(v)
        return V

    @staticmethod
    def AND(V_in, V_out):
        # (0, 0) -> 0, (0, 1) -> 0, (1, 0) -> 0, (1, 1) -> 1
        m = len(V_in)
        constr = []
        constr = constr + [V_out + ' - ' + BasicTools.minusTerms(V_in) + ' >= ' + str(1 - m)]
        constr = constr + [BasicTools.plusTerms(V_in) + ' - ' + str(m) + ' ' + V_out + ' >= 0']
        return constr

    @staticmethod
    def OR_(V_in, V_out):
        # (0, 0) -> 0, (0, 1) -> 1, (1, 0) -> 1, (1, 1) -> 1
        m = len(V_in)
        constr = []
        constr = constr + [str(m) + ' ' + V_out + ' - ' + BasicTools.minusTerms(V_in) + ' >= 0']
        constr = constr + [V_out + ' - ' + BasicTools.minusTerms(V_in) + ' <= 0']
        return constr

    @staticmethod
    def N_AND(V_in, V_out):
        # (0, 0) -> 1, (0, 1) -> 1, (1, 0) -> 1, (1, 1) -> 0
        m = len(V_in)
        constr = []
        constr = constr + [V_out + ' + ' + BasicTools.plusTerms(V_in) + ' <= ' + str(m)]
        constr = constr + [BasicTools.plusTerms(V_in) + ' + ' + str(m) + ' ' + V_out + ' >= ' + str(m)]
        return constr

    @staticmethod
    def N_OR_(V_in, V_out):
        # (0, 0) -> 1, (0, 1) -> 0, (1, 0) -> 0, (1, 1) -> 0
        m = len(V_in)
        constr = []
        if m != 0:
            constr = constr + [V_out + ' + ' + BasicTools.plusTerms(V_in) + ' >= 1']
            for j in range(m):
                constr = constr + [V_in[j] + ' + ' + V_out + ' <= 1']
        elif m == 0:
            constr = constr + [V_out + ' >= 1']
        return constr


class MITMPreConstraints:
    @staticmethod
    def Determine_Allone(V_in, V_out):
        m = len(V_in)
        constr = []
        constr = constr + [V_out + ' - ' + BasicTools.minusTerms(V_in) + ' >= ' + str(1 - m)]
        constr = constr + [BasicTools.plusTerms(V_in) + ' - ' + str(m) + ' ' + V_out + ' >= 0']
        return constr

    @staticmethod
    def Determine_Allzero(V_in, V_out):
        m = len(V_in)
        constr = []
        constr = constr + [V_out + ' + ' + BasicTools.plusTerms(V_in) + ' >= 1']
        for j in range(m):
            constr = constr + [V_in[j] + ' + ' + V_out + ' <= 1']
        return constr

    @staticmethod
    def Separate(
            In_1_i,
            In_2_i,
            SupP_Blue_1_i,
            SupP_Blue_2_i,
            SupP_Red__1_i,
            SupP_Red__2_i,
            In_isWhite_i
    ):
        cons = []
        cons = cons + BasicTools.N_OR_([In_1_i, In_2_i], In_isWhite_i)
        cons = cons + [SupP_Blue_1_i + ' + ' + In_isWhite_i + ' = 1']
        cons = cons + [SupP_Blue_2_i + ' - ' + In_2_i + ' = 0']
        cons = cons + [SupP_Red__2_i + ' - ' + SupP_Blue_1_i + ' = 0']
        cons = cons + [SupP_Red__1_i + ' - ' + In_1_i + ' = 0']
        return cons

    #用于ARIA
    @staticmethod
    def genSubConstraints_7Xor_SupP_Blue(
            I_MC_SupP_Blue_1_coli,
            I_MC_SupP_Blue_2_coli,
            I_MC_SupP_Blue_ColExistWhite_coli,
            I_MC_SupP_Blue_ColAllGray_coli,
            O_MC_SupP_Blue_1_coli,
            O_MC_SupP_Blue_2_coli,
            CD_MC_Blue_coli
    ):
        cons = []
        for Ri in range(RowN):
            sum_x = []
            sum_y = []
            for i in P[Ri]:
                sum_x = sum_x + [I_MC_SupP_Blue_1_coli[i]]
                sum_y = sum_y + [I_MC_SupP_Blue_2_coli[i]]
            n = 7
            cons = cons + [BasicTools.plusTerms(sum_x) + ' + ' + I_MC_SupP_Blue_ColExistWhite_coli[Ri] + ' <= ' + str(n)]
            cons = cons + [BasicTools.plusTerms(sum_x) + ' + ' + str(n) + ' ' + I_MC_SupP_Blue_ColExistWhite_coli[Ri] + ' >= ' + str(n)]
            cons = cons + [BasicTools.plusTerms(sum_y) + ' - ' + I_MC_SupP_Blue_ColAllGray_coli[Ri] + ' <= ' + str(n-1)]
            cons = cons + [BasicTools.plusTerms(sum_y) + ' - ' + str(n) + ' ' + I_MC_SupP_Blue_ColAllGray_coli[Ri] + ' >= 0']
            cons = cons + [O_MC_SupP_Blue_1_coli[Ri] + ' + ' + I_MC_SupP_Blue_ColExistWhite_coli[Ri] + ' = 1']
            cons = cons + [O_MC_SupP_Blue_2_coli[Ri] + ' + ' + I_MC_SupP_Blue_ColExistWhite_coli[Ri] + ' <= 1']
            cons = cons + [CD_MC_Blue_coli[Ri] + ' - ' + O_MC_SupP_Blue_2_coli[Ri] + ' + ' + I_MC_SupP_Blue_ColAllGray_coli[Ri] + ' = 0']
            cons = cons + [BasicTools.plusTerms(sum_y) + ' + ' + O_MC_SupP_Blue_2_coli[Ri] + ' - 2 ' + I_MC_SupP_Blue_ColAllGray_coli[Ri] + ' <= ' + str(n-1)]
            cons = cons + [BasicTools.plusTerms(sum_y) + ' + ' + O_MC_SupP_Blue_2_coli[Ri] + ' - ' + str(n+1) + ' ' + I_MC_SupP_Blue_ColAllGray_coli[Ri] + ' >= 0']
        return cons

    @staticmethod
    def genSubConstraints_7Xor_SupP_Red(
            I_MC_SupP_Red_1_coli,
            I_MC_SupP_Red_2_coli,
            I_MC_SupP_Red_ColExistWhite_coli,
            I_MC_SupP_Red_ColAllGray_coli,
            O_MC_SupP_Red_1_coli,
            O_MC_SupP_Red_2_coli,
            CD_MC_Red_coli
    ):
        cons = []
        for Ri in range(RowN):
            sum_x = []
            sum_y = []
            for i in P[Ri]:
                sum_x = sum_x + [I_MC_SupP_Red_1_coli[i]]
                sum_y = sum_y + [I_MC_SupP_Red_2_coli[i]]
            n = 7
            cons = cons + [BasicTools.plusTerms(sum_y) + ' + ' + I_MC_SupP_Red_ColExistWhite_coli[Ri] + ' <= ' + str(n)]
            cons = cons + [
                BasicTools.plusTerms(sum_y) + ' + ' + str(n) + ' ' + I_MC_SupP_Red_ColExistWhite_coli[
                    Ri] + ' >= ' + str(n)]
            cons = cons + [
                BasicTools.plusTerms(sum_x) + ' - ' + I_MC_SupP_Red_ColAllGray_coli[Ri] + ' <= ' + str(n - 1)]
            cons = cons + [
                BasicTools.plusTerms(sum_x) + ' - ' + str(n) + ' ' + I_MC_SupP_Red_ColAllGray_coli[Ri] + ' >= 0']
            cons = cons + [O_MC_SupP_Red_2_coli[Ri] + ' + ' + I_MC_SupP_Red_ColExistWhite_coli[Ri] + ' = 1']
            cons = cons + [O_MC_SupP_Red_1_coli[Ri] + ' + ' + I_MC_SupP_Red_ColExistWhite_coli[Ri] + ' <= 1']
            cons = cons + [
                CD_MC_Red_coli[Ri] + ' - ' + O_MC_SupP_Red_1_coli[Ri] + ' + ' + I_MC_SupP_Red_ColAllGray_coli[
                    Ri] + ' = 0']
            cons = cons + [BasicTools.plusTerms(sum_x) + ' + ' + O_MC_SupP_Red_1_coli[Ri] + ' - 2 ' +
                           I_MC_SupP_Red_ColAllGray_coli[Ri] + ' <= ' + str(n - 1)]
            cons = cons + [BasicTools.plusTerms(sum_x) + ' + ' + O_MC_SupP_Red_1_coli[Ri] + ' - ' + str(n + 1) + ' ' +
                           I_MC_SupP_Red_ColAllGray_coli[Ri] + ' >= 0']
        return cons
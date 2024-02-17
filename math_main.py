from utils import *
from gurobipy import *


class Vars_generator:
    # Initial state
    @staticmethod
    def genVars_degree_forward():
        return ['deg_f_' + str(j) for j in range(bs)]
    @staticmethod
    def genVars_degree_backward():
        return ['deg_b_' + str(j) for j in range(bs)]

    # Input coordinates for each round
    @staticmethod
    def genVars_Input_of_Round(index, round):
        return [f'IP_{index}_r{round}_{j}' for j in range(bs)]

    # State separation
    @staticmethod
    def genVars_SupP_Blue_Input_of_Round(index, round):
        return [f'IP_SupP_Blue_{index}_r{round}_{j}' for j in range(bs)]
    @staticmethod
    def genVars_SupP_Red_Input_of_Round(index, round):
        return [f'IP_SupP_Red_{index}_r{round}_{j}' for j in range(bs)]
    @staticmethod
    def genVars_SupP_Blue_Output_of_MixColumns(index, round):
        return [f'OMC_SupP_Blue_{index}_r{round}_{j}' for j in range(bs)]
    @staticmethod
    def genVars_SupP_Red_Output_of_MixColumns(index, round):
        return [f'OMC_SupP_Red_{index}_r{round}_{j}' for j in range(bs)]
    # Flag bit
    @staticmethod
    def genVars_Match_IsWhite(round):
        return [f'Match_IW_r{round}_{j}' for j in range(bs)]


class Constraints_generator:
    def __init__(self, total_round):
        self.TR = total_round

    def genModel(self, filename):
        cons = []
        cons = cons + self.genConstraints_total()
        cons = cons + ['GObj - GDeg1 <= 0']
        cons = cons + ['GObj - GDeg2 <= 0']
        cons = cons + ['GObj - GMat <= 0']
        cons = cons + ['GObj >= 1']

        V = BasicTools.getVariables_From_Constraints(cons)
        with open(filename + ".lp", "w") as fid:
            fid.write('Maximize multi-objectives' + '\n')
            index = 0
            fid.write(f'OBJ{index}: Priority=0 Weight=1 AbsTol=1e-06 RelTol=0' + '\n')
            fid.write(f'GObj' + '\n')
            index += 1
            for r in range(self.TR):
                fid.write(f'OBJ{index}: Priority=0 Weight=1 AbsTol=1e-06 RelTol=0' + '\n')
                index += 1
                fid.write(f'GCD_r{r}_Blue' + '\n')
                fid.write(f'OBJ{index}: Priority=0 Weight=1 AbsTol=1e-06 RelTol=0' + '\n')
                index += 1
                fid.write(f'GCD_r{r}_Red' + '\n')
            fid.write('\n')
            fid.write('Subject To')
            fid.write('\n')
            for c in cons:
                fid.write(c)
                fid.write('\n')
            GV = []
            BV = []
            Bound = []
            for v in V:
                if v[0] == 'G':
                    GV.append(v)
                elif v[0] == 'B':
                    Bound.append(v)
                else:
                    BV.append(v)
            fid.write('Bounds' + '\n')
            for bo in Bound:
                fid.write('-10 <= ' + bo + ' <= 10' + '\n')
            fid.write('Binary' + '\n')
            for bv in BV:
                fid.write(bv + '\n')
            fid.write('Generals' + '\n')
            for gv in GV:
                fid.write(gv + '\n')
            for gv in Bound:
                fid.write(gv + '\n')

    def genConstraints_total(self):
        cons = []
        cons = cons + self.genConstraints_initial_degree()
        for r in range(self.TR):
            cons = cons + self.genConstraints_one_round(r)
        cons = cons + self.genConstraints_Match()
        cons = cons + self.genConstraints_additional()
        return cons

    def genConstraints_initial_degree(self):
        cons = []
        d1 = Vars_generator.genVars_degree_forward()
        d2 = Vars_generator.genVars_degree_backward()
        IP_1 = Vars_generator.genVars_Input_of_Round(1, 0)
        IP_2 = Vars_generator.genVars_Input_of_Round(2, 0)

        for bi in range(bs):
            cons = cons + [IP_1[bi] + ' + ' + IP_2[bi] + ' >= 1']
            cons = cons + [d1[bi] + ' + ' + IP_2[bi] + ' = 1']
            cons = cons + [d2[bi] + ' + ' + IP_1[bi] + ' = 1']
        return cons

    def genConstraints_one_round(self, r):
        cons = []
        IP_1 = Vars_generator.genVars_Input_of_Round(1, r)
        IP_2 = Vars_generator.genVars_Input_of_Round(2, r)
        IP_SupP_Blue_1 = Vars_generator.genVars_SupP_Blue_Input_of_Round(1, r)
        IP_SupP_Blue_2 = Vars_generator.genVars_SupP_Blue_Input_of_Round(2, r)
        IP_SupP_Red_1 = Vars_generator.genVars_SupP_Red_Input_of_Round(1, r)
        IP_SupP_Red_2 = Vars_generator.genVars_SupP_Red_Input_of_Round(2, r)
        IP_isWhite = [f'IP_isWhite_r{r}_{j}' for j in range(bs)]
        OMC_SupP_Blue_1 = Vars_generator.genVars_SupP_Blue_Output_of_MixColumns(1, r)
        OMC_SupP_Blue_2 = Vars_generator.genVars_SupP_Blue_Output_of_MixColumns(2, r)
        OMC_SupP_Red_1 = Vars_generator.genVars_SupP_Red_Output_of_MixColumns(1, r)
        OMC_SupP_Red_2 = Vars_generator.genVars_SupP_Red_Output_of_MixColumns(2, r)
        OP_1 = Vars_generator.genVars_Input_of_Round(1, r + 1)
        OP_2 = Vars_generator.genVars_Input_of_Round(2, r + 1)
        # Flag bit
        IMC_SupP_Blue_ColExistWhite = [f'MC_SupP_Blue_ColExistWhite_r{r}_{i}' for i in range(bs)]
        IMC_SupP_Red_ColExistWhite = [f'MC_SupP_Red_ColExistWhite_r{r}_{i}' for i in range(bs)]
        IMC_SupP_Blue_ColAllGray = [f'MC_SupP_Blue_ColAllGray_r{r}_{i}' for i in range(bs)]
        IMC_SupP_Red_ColAllGray = [f'MC_SupP_Red_ColAllGray_r{r}_{i}' for i in range(bs)]
        Xor_Blue = [f'Xor_MC_Blue_r{r}_{i}' for i in range(bs)]
        Xor_Red = [f'Xor_MC_Red_r{r}_{i}' for i in range(bs)]
        # Find the rank of a particular matrix
        M_Blue = [[f'M[{i},{j}]_r{r}_Blue' for j in range(qq)] for i in range(pp)]
        e_borrowed_Blue = [f'e_borrowed[{i}]_r{r}_Blue' for i in range(pp)]
        scalars_Blue = [[f'B_scalars[{i},{j}]_r{r}_Blue' for j in range(pp)] for i in range(qq)]
        e_scalars_Blue = [[f'B_e_scalars[{i},{j}]_r{r}_Blue' for j in range(pp)] for i in range(pp)]
        M_Red = [[f'M[{i},{j}]_r{r}_Red' for j in range(qq)] for i in range(pp)]
        e_borrowed_Red = [f'e_borrowed[{i}]_r{r}_Red' for i in range(pp)]
        scalars_Red = [[f'B_scalars[{i},{j}]_r{r}_Red' for j in range(pp)] for i in range(qq)]
        e_scalars_Red = [[f'B_e_scalars[{i},{j}]_r{r}_Red' for j in range(pp)] for i in range(pp)]

        # State separation
        for bi in range(bs):
            cons = cons + MITMPreConstraints.Separate(
                IP_1[bi],
                IP_2[bi],
                IP_SupP_Blue_1[bi],
                IP_SupP_Blue_2[bi],
                IP_SupP_Red_1[bi],
                IP_SupP_Red_2[bi],
                IP_isWhite[bi]
            )
        # Diffusion operation
        cons = cons + MITMPreConstraints.genSubConstraints_7Xor_SupP_Blue(
            IP_SupP_Blue_1,
            IP_SupP_Blue_2,
            IMC_SupP_Blue_ColExistWhite,
            IMC_SupP_Blue_ColAllGray,
            OMC_SupP_Blue_1,
            OMC_SupP_Blue_2,
            Xor_Blue
        )
        cons = cons + MITMPreConstraints.genSubConstraints_7Xor_SupP_Red(
            IP_SupP_Red_1,
            IP_SupP_Red_2,
            IMC_SupP_Red_ColExistWhite,
            IMC_SupP_Red_ColAllGray,
            OMC_SupP_Red_1,
            OMC_SupP_Red_2,
            Xor_Red
        )
        # Find the rank of a particular matrix
        for i in range(pp):
            for j in range(qq):
                if DL[i][j] == 0:
                    cons = cons + [M_Blue[i][j] + ' = 0']
                elif DL[i][j] == 1:
                    cons = cons + [
                        M_Blue[i][j] + ' + [ - ' + Xor_Blue[i] + ' * ' + IP_SupP_Blue_1[j] + ' + ' + Xor_Blue[i] + ' * ' + IP_SupP_Blue_2[j] + ' ] = 0'
                    ]
        result = [[''] * pp for _ in range(pp)]
        for i in range(pp):
            for j in range(pp):
                for k in range(qq):
                    result[i][j] += M_Blue[i][k] + ' * ' + scalars_Blue[k][j] + ' + '
        for i in range(pp):
            for j in range(pp):
                cons = cons + [
                    e_scalars_Blue[i][j] + ' + [ ' + result[i][j][0:-3] + ' ] = ' + str(identity[i][j])
                ]

        for i in range(pp):
            for j in range(pp):
                cons = cons + [
                    e_borrowed_Blue[i] + ' = 0 -> ' + e_scalars_Blue[i][j] + ' = 0'
                ]
        cons = cons + [
            f'GCD_r{r}_Blue + ' + BasicTools.plusTerms(e_borrowed_Blue) + ' = ' + str(pp)
        ]

        for i in range(pp):
            for j in range(qq):
                if DL[i][j] == 0:
                    cons = cons + [M_Red[i][j] + ' = 0']
                elif DL[i][j] == 1:
                    cons = cons + [
                        M_Red[i][j] + ' + [ - ' + Xor_Red[i] + ' * ' + IP_SupP_Red_2[j] + ' + ' + Xor_Red[i] + ' * ' + IP_SupP_Red_1[j] + ' ] = 0'
                    ]
        result = [[''] * pp for _ in range(pp)]
        for i in range(pp):
            for j in range(pp):
                for k in range(qq):
                    result[i][j] += M_Red[i][k] + ' * ' + scalars_Red[k][j] + ' + '
        for i in range(pp):
            for j in range(pp):
                cons = cons + [
                    e_scalars_Red[i][j] + ' + [ ' + result[i][j][0:-3] + ' ] = ' + str(identity[i][j])
                ]

        for i in range(pp):
            for j in range(pp):
                cons = cons + [
                    e_borrowed_Red[i] + ' = 0 -> ' + e_scalars_Red[i][j] + ' = 0'
                ]
        cons = cons + [
            f'GCD_r{r}_Red + ' + BasicTools.plusTerms(e_borrowed_Red) + ' = ' + str(pp)
        ]

        # Merge state
        for bi in range(bs):
            cons = cons + MITMPreConstraints.Determine_Allone([OMC_SupP_Blue_1[bi],OMC_SupP_Red_1[bi]],OP_1[bi])
            cons = cons + MITMPreConstraints.Determine_Allone([OMC_SupP_Blue_2[bi], OMC_SupP_Red_2[bi]],
                                                              OP_2[bi])
        return cons

    def genConstraints_Match(self):
        cons = []
        IP_r_1 = Vars_generator.genVars_Input_of_Round(1, 0)
        IP_r_2 = Vars_generator.genVars_Input_of_Round(2, 0)
        IP_next_r_1 = Vars_generator.genVars_Input_of_Round(1, self.TR)
        IP_next_r_2 = Vars_generator.genVars_Input_of_Round(2, self.TR)
        IW_r = Vars_generator.genVars_Match_IsWhite(0)
        IW_next_r = Vars_generator.genVars_Match_IsWhite(self.TR)
        Match = [f'Match_{j}' for j in range(bs)]
        GMat = 'GMat'

        for bi in range(bs):
            cons = cons + MITMPreConstraints.Determine_Allzero([IP_r_1[bi], IP_r_2[bi]], IW_r[bi])
            cons = cons + MITMPreConstraints.Determine_Allzero([IP_next_r_1[bi], IP_next_r_2[bi]], IW_next_r[bi])
        for bi in range(bs):
            cons =cons + BasicTools.N_OR_([IW_r[bi], IW_next_r[bi]], Match[bi])
        cons = cons + [GMat + ' - ' + BasicTools.minusTerms(Match) + ' = 0']
        cons = cons + ['GMat >= 1']
        return cons

    def genConstraints_additional(self):
        cons = []
        CD_Blue = []
        CD_Red = []
        for r in range(self.TR):
            CD_Blue = CD_Blue + [f'GCD_r{r}_Blue']
            CD_Red = CD_Red + [f'GCD_r{r}_Red']
        d1 = Vars_generator.genVars_degree_forward()
        d2 = Vars_generator.genVars_degree_backward()
        Deg1 = 'GDeg1'
        Deg2 = 'GDeg2'

        cons = cons + [
            Deg1 + ' - ' + BasicTools.minusTerms(d1) + ' + ' + BasicTools.plusTerms(CD_Blue) + ' = 0']
        cons = cons + [
            Deg2 + ' - ' + BasicTools.minusTerms(d2) + ' + ' + BasicTools.plusTerms(CD_Red) + ' = 0']
        cons = cons + [Deg1 + ' >= 1']
        cons = cons + [Deg2 + ' >= 1']
        return cons


if __name__ == '__main__':
    TR = 2
    root = f'./Model'
    if not os.path.exists(root):
        os.mkdir(root)

    filename = f'./Model/TR{TR}'
    A = Constraints_generator(TR)
    A.genModel(filename)
    Model = read(filename + '.lp')
    Model.optimize()
    Model.write(filename + '.sol')
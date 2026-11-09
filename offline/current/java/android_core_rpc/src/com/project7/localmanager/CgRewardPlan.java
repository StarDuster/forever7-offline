package com.project7.localmanager;
/** Generated from pinned public tables by project7_cg_rewards/produce.py. */
final class CgRewardPlan {
    static final String SHA256 = "647a1ec62aa56d87a291ce1b9121cbd3a97cf5c00fa71e97d1f6e1d283080675";
    static final int ITEM = 329, AMOUNT = 700;
    private static final int[][] LINES = {
        {1,11,13},
        {2,46,47},
        {3,20,21},
        {4,93,94,95},
        {5,104,105},
        {6,125,126,127},
        {7,136,137},
        {8,147,148,149,150},
        {9,159,160,161},
        {10,162,163},
        {11,184,185,186},
        {12,202,203},
        {13,214,215,216},
        {14,226,227},
        {15,240,241,242},
        {16,256,257,258},
        {17,271,272},
        {18,281,282},
        {19,298,299},
        {20,313,312},
        {21,323,324},
        {22,337,338,339},
        {23,356,357},
        {24,371,370},
        {25,382,383},
        {26,398,399},
        {27,413,414},
        {28,417,418},
        {29,432,433},
        {30,442,443},
        {31,450,451},
        {32,465,466}
    };
    static boolean eligible(int line, int cg) {
        for (int[] row : LINES) if (row[0] == line) {
            for (int i=1;i<row.length;i++) if (row[i]==cg) return true;
            return false;
        }
        return false;
    }
    private CgRewardPlan() {}
}

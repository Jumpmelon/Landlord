#ifndef MAIN_H
#define MAIN_H

#include <bits/stdc++.h>
#include "card.h"

int getBidValue(int maxBid); // 叫分
CardCombo getAction(); // 出牌, 搜索记得维护全局变量
// double getMean(); // 根据当前牌得到最优策略得分期望

int search(); // 最优得分
std::vector<CardCombo> getCandidates();
std::vector<std::pair<CardDistrib, double>> randCards(int num, double TL);
std::vector<std::pair<double, CardCombo>> getCandidatesEval(int num, bool worstCase = 0);
double getCandidateProb(const CardCombo &);
double evalCards(const CardSet &); // 期望得分
double eval(const CardCombo &, bool worstCase = 0); // 期望得分

CardSet cardSub(const CardSet &s, const CardCombo &c);
CardSet cardAdd(const CardSet &s, const CardCombo &c);

void doCombo(const CardCombo &c);
void undoCombo();

#endif

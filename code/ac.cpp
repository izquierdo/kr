#include <vector>
#include <iostream>
#include <map>
#include <set>
#include <fstream>
#include <iterator>

using namespace std;

typedef vector<pair<char, vector<int> > > nnf_t;
typedef map<string, string> evidence_t;

class AC {
private:
  void init(istream &in){
    string nnffile;
    int lcount, tcount;
    in >> nnffile >> lcount >> tcount;
    ifstream f(nnffile.c_str());
    // cout << "reading nnf" << endl;

    string header;
    int v, e, n;
    f >> header >> v >> e >> n;
    // cout << header << " " << v << " " << e << " " << n << endl;
    nnf.resize(v);
    for (int i=0; i<v ; ++i){
      string type;
      f >> type;
      nnf[i].first = type[0];
      if (type[0] == 'L'){
        int x;
        f >> x;
        nnf[i].second.push_back(x);
      } else if (type[0] == 'A'){
        int childcount;
        f >> childcount;
        nnf[i].second.resize(childcount);
        for (int j=0; j<childcount; ++j){
          f >> nnf[i].second[j];
        }
      } else if (type[0] == 'O'){
        int childcount, conflict;
        f >> conflict >> childcount;
        nnf[i].second.resize(childcount);
        for (int j=0; j<childcount; ++j){
          f >> nnf[i].second[j];
        }
      }
    }

    for (int i=0; i<lcount; ++i){
      int id;
      string name, value;
      in >> id >> name >> value;
      lambda[id] = make_pair(name, value);
      // cout << id << "->" << lambda[id].first << endl;
    }

    for (int i=0; i<tcount; ++i){
      int id;
      double p;
      in >> id >> p;
      theta[id] = p;
    }

  }

  double varvalue(int varid, const evidence_t &e) const {
    if (varid < 0)
      return 1;

    map<int,double>::const_iterator it = theta.find(varid);
    if (it != theta.end())
      return it->second;

    map<int, pair<string, string> >::const_iterator il = lambda.find(varid);
    // assert(il!=lambda.end());
    evidence_t::const_iterator ie = e.find(il->second.first);
    if (ie == e.end() || ie->second == il->second.second){
      return 1;
    }
    return 0.0;
  }

public:
  nnf_t nnf;
  map<int, double> theta;
  map<int, pair<string, string> > lambda;

  AC(char *filename){
    ifstream in (filename);
    init(in);
  }

  AC(istream &in){
    init(in);
  }

  double mpe() const {
    evidence_t e;
    return mpe(e);
  }
  
  double mpe(const evidence_t &e) const {
    vector<double> probs;
    probs.reserve(nnf.size());
    int id = 0;
    for (nnf_t::const_iterator i = nnf.begin(); i != nnf.end(); ++i, ++id){
      if (i->first == 'L'){
        probs.push_back(varvalue(i->second.front(), e));

      } else if (i->first=='A'){
        double p = 1;
        for (vector<int>::const_iterator j = i->second.begin();
             j != i->second.end();
             ++j){
          p *= probs[*j];
        }
        probs.push_back(p);
      } else if (i->first=='O'){
        double p = -1;
        for (vector<int>::const_iterator j = i->second.begin();
             j != i->second.end();
             ++j){
          p = max(probs[*j], p);
        }
        probs.push_back(p);
      }
    }
    return probs.back();
  }
};

int main(){
  AC ac(cin);
  evidence_t ee;
  cout << "MPE:" << ac.mpe(ee) << endl;

  return 0;
}

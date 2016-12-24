package com.example.ladenheim.beerratings;

import android.app.Fragment;
import android.app.ProgressDialog;
import android.os.AsyncTask;
import android.os.SystemClock;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.ListAdapter;
import android.widget.ListView;
import android.widget.SearchView;
import android.widget.TextView;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class SearchActivity extends AppCompatActivity {

    private static String LOG_TAG = SearchActivity.class.getSimpleName();
    ListView listView = null;
    public PlaceAdapter adapter = null;
    // GpsFinder gpsFinder = null;


    class SearchTask extends AsyncTask<String, Void, List<Beer>> {
        ProgressDialog progress = null;

        @Override
        protected void onPreExecute() {
            super.onPreExecute();
            progress = new ProgressDialog(SearchActivity.this);
            progress.setTitle("Searching");
            progress.setMessage("In Progress");
            progress.show();
        }

        @Override
        protected List<Beer> doInBackground(String... params) {
            try {
                final List<Beer> beers = ApiUtils.getBeers(params[0]);
                if(beers == null) {
                    progress.dismiss();
                    return null;
                }
                SearchActivity.this.runOnUiThread(new Runnable() {
                    @Override
                    public void run() {
                        // findViewById(R.id.not_found_txt).setVisibility(View.GONE);
                        adapter.setList(beers);
                        listView.setVisibility(View.VISIBLE);
                    }
                });
                return beers;

            } catch (IOException ex) {
                Log.d(LOG_TAG, ex.getMessage());
                ex.printStackTrace();
                return null;
            }
        }

        @Override
        protected void onPostExecute(List<Beer> result) {
            if(progress.isShowing()) {
                progress.dismiss();
            }
        }
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_search);

        List<Beer> beers = Arrays.asList(
                new Beer("bud light limarita", 5.1, 4.9), new Beer("molsens", 1.0, 1.3), new Beer("sminoff ice", 2.1, 4.4));

        adapter = new PlaceAdapter(this, beers);

        listView = (ListView) findViewById(R.id.list_view);
        listView.setAdapter(adapter);
        adapter.notifyDataSetChanged();

        final SearchView searchView = (SearchView) findViewById(R.id.search_text);

        Button searchButton = (Button) findViewById(R.id.search_button);
        searchButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                new SearchTask().execute(searchView.getQuery().toString());
            }
        });

        TextView nameLabel = (TextView) findViewById(R.id.name_label);
        nameLabel.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                adapter.sortByName();
            }
        });
        TextView ratingLabel = (TextView) findViewById(R.id.ba_rating_label);
        ratingLabel.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                adapter.sortByRating();
            }
        });

    }


    @Override
    public void onSaveInstanceState(Bundle savedInstanceState) {
        super.onSaveInstanceState(savedInstanceState);
    }

    public void onRestoreInstanceState(Bundle savedInstanceState) {
        super.onRestoreInstanceState(savedInstanceState);
    }


}
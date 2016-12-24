package com.example.ladenheim.beerratings;

import android.content.Context;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.TextView;

import org.w3c.dom.Text;

import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;

/**
 * Created by ladenheim on 10/3/16.
 */
public class PlaceAdapter extends ArrayAdapter<Beer> {

    private Context context;
    private List<Beer> beers;


    private static class PlaceViewHolder {
        Beer beer;
        TextView name;
        TextView rating;
        int position;
    }

    public PlaceAdapter(Context context, List<Beer> beers) {
        super(context, R.layout.fragment_beer, beers);
        this.context = context;
        this.beers = beers;
    }

    public void setList(List<Beer> beers) {
        this.beers = beers;
        this.notifyDataSetChanged();
    }

    public void sortByRating() {
        Collections.sort(this.beers, new Comparator<Beer>() {
            @Override
            public int compare(Beer b1, Beer b2) {
                // There are three decimal places in rating.
                return (int)(b2.ratingBeerAdvocate*100 - b1.ratingBeerAdvocate*100);
            }
        });
        notifyDataSetChanged();
    }

    public void sortByName() {
        Collections.sort(this.beers, new Comparator<Beer>() {
            @Override
            public int compare(Beer b1, Beer b2) {
                // There are three decimal places in rating.
                return b1.name.compareTo(b2.name);
            }
        });
        notifyDataSetChanged();
    }


    @Override
    public void notifyDataSetChanged() {
//        this.setNotifyOnChange(false);
//        this.sort(new Comparator<Beer>() {
//            @Override
//            public int compare(Beer b1, Beer b2) {
//                // There are three decimal places in rating.
//                return (int)(b2.ratingBeerAdvocate*100 - b1.ratingBeerAdvocate*100);
//            }
//        });
//        this.setNotifyOnChange(true);
        super.notifyDataSetChanged();
    }

    @Override
    public View getView(final int position, View convertView, ViewGroup parent) {
        if(convertView == null) {
            convertView = LayoutInflater.from(context).inflate(R.layout.fragment_beer, null);
        }

        Beer beer = beers.get(position);
        TextView beerName = (TextView) convertView.findViewById(R.id.beer_name);
        beerName.setText(beer.name);
        TextView ratingBeerAdvocate = (TextView) convertView.findViewById(R.id.rating_ba);
        ratingBeerAdvocate.setText(Double.toString(beer.ratingBeerAdvocate));
        //TextView ratingUntappd = (TextView) convertView.findViewById(R.id.rating_untappd);
        //ratingUntappd.setText(Double.toString(beer.ratingUntappd));
        return convertView;
    }

    @Override
    public int getCount() {
        return beers.size();
    }

    @Override
    public Beer getItem(int position) {
        return beers.get(position);
    }

    @Override
    public long getItemId(int position) {
        return 0;
    }
}

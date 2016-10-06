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
        notifyDataSetChanged();
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
        TextView ratingUntappd = (TextView) convertView.findViewById(R.id.rating_untappd);
        ratingUntappd.setText(Double.toString(beer.ratingUntappd));
        return convertView;
    }



}

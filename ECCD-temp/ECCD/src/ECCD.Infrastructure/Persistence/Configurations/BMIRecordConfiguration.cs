using ECCD.Domain.Entities;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace ECCD.Infrastructure.Persistence.Configurations;

public class BMIRecordConfiguration : IEntityTypeConfiguration<BMIRecord>
{
    public void Configure(EntityTypeBuilder<BMIRecord> builder)
    {
        builder.HasKey(b => b.Id);

        builder.Property(b => b.HeightCm).HasPrecision(5, 2);
        builder.Property(b => b.WeightKg).HasPrecision(5, 2);
        builder.Property(b => b.Bmi).HasPrecision(5, 2);
        builder.Property(b => b.WhoZScore).HasPrecision(5, 2);

        builder.HasOne(b => b.Learner)
            .WithMany(l => l.BmiRecords)
            .HasForeignKey(b => b.LearnerId)
            .OnDelete(DeleteBehavior.Cascade);

        builder.HasIndex(b => new { b.LearnerId, b.Date });
    }
}
